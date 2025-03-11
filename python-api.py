from flask import Flask, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)  # Added numeric field for better range demonstration

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help="Name cannot be blank!")
parser.add_argument('description', required=True, help="Description cannot be blank!")
parser.add_argument('price', type=float, required=True, help="Price must be a number!")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'price': fields.Float,
}

class ItemResource(Resource):
    @marshal_with(resource_fields)
    def get(self, item_id=None):
        if item_id:
            item = Item.query.get_or_404(item_id)
            return item
        else:
            # Get filter parameters from query string
            min_id = request.args.get('min_id')
            max_id = request.args.get('max_id')
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            
            query = Item.query
            
            # ID range filtering
            if min_id:
                query = query.filter(Item.id >= min_id)
            if max_id:
                query = query.filter(Item.id <= max_id)
            
            # Price range filtering
            if min_price:
                query = query.filter(Item.price >= min_price)
            if max_price:
                query = query.filter(Item.price <= max_price)
            
            items = query.all()
            return items

    @marshal_with(resource_fields)
    def post(self):
        args = parser.parse_args()
        item = Item(
            name=args['name'],
            description=args['description'],
            price=args['price']
        )
        db.session.add(item)
        db.session.commit()
        return item, 201

    @marshal_with(resource_fields)
    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        args = parser.parse_args()
        item.name = args['name']
        item.description = args['description']
        db.session.commit()
        return item

    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

api.add_resource(ItemResource, '/items', '/items/<int:item_id>')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
