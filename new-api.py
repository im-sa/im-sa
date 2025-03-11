from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize Flask
app = Flask(__name__)
api = Api(app)

# Configure SQLAlchemy engine for existing SQLite database
DATABASE_URI = 'sqlite:///existing.db'  # Update with your database path
engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define model matching existing table
class Item(Base):
    __tablename__ = 'items'  # Must match your table name
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(200))
    price = Column(Float)  # Adjust fields to match your table

# Request parser setup
parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('description', required=True)
parser.add_argument('price', type=float, required=True)

# Response formatting
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'price': fields.Float,
}

class ItemResource(Resource):
    @marshal_with(resource_fields)
    def get(self, item_id=None):
        session = Session()
        try:
            if item_id:
                item = session.query(Item).get(item_id)
                if not item:
                    abort(404, message="Item not found")
                return item
            else:
                # Handle range filters
                query = session.query(Item)
                
                if request.args.get('min_id'):
                    query = query.filter(Item.id >= int(request.args['min_id']))
                if request.args.get('max_id'):
                    query = query.filter(Item.id <= int(request.args['max_id']))
                if request.args.get('min_price'):
                    query = query.filter(Item.price >= float(request.args['min_price']))
                if request.args.get('max_price'):
                    query = query.filter(Item.price <= float(request.args['max_price']))
                
                return query.all()
        finally:
            session.close()

    @marshal_with(resource_fields)
    def post(self):
        args = parser.parse_args()
        session = Session()
        try:
            item = Item(
                name=args['name'],
                description=args['description'],
                price=args['price']
            )
            session.add(item)
            session.commit()
            return item, 201
        except Exception as e:
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()

    # Add similar implementations for put and delete methods

api.add_resource(ItemResource, '/items', '/items/<int:item_id>')

if __name__ == '__main__':
    app.run(debug=True)
