pip install fastapi sqlmodel uvicorn
uvicorn main:app --reload
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

# Define the Hero model
class Hero(SQLModel, table=True):
    id: int | None = None
    name: str
    secret_name: str
    age: int | None = None

# Database setup
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)

app = FastAPI()

# Create database tables on startup
@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Create Hero endpoint
@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero

# Get all Heroes endpoint
@app.get("/heroes/", response_model=list[Hero])
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes

# Get single Hero endpoint
@app.get("/heroes/{hero_id}", response_model=Hero)
def read_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero

# Update Hero endpoint
@app.put("/heroes/{hero_id}", response_model=Hero)
def update_hero(hero_id: int, hero: Hero):
    with Session(engine) as session:
        db_hero = session.get(Hero, hero_id)
        if not db_hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        
        hero_data = hero.dict(exclude_unset=True)
        for key, value in hero_data.items():
            setattr(db_hero, key, value)
            
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero

# Delete Hero endpoint
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        session.delete(hero)
        session.commit()
        return {"message": "Hero deleted successfully"}
