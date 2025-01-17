
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Restaurants(Resource):
    def get(self):
        restaurants = [{"id": r.id, "name": r.name, "address": r.address} for r in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return make_response(jsonify({
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": [{
                    "id": rp.id,
                    "price": rp.price,
                    "pizza_id": rp.pizza_id,
                    "restaurant_id": rp.restaurant_id,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                } for rp in restaurant.restaurant_pizzas]
            }), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

class Pizzas(Resource):
    def get(self):
        pizzas = [{"id": p.id, "name": p.name, "ingredients": p.ingredients} for p in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            
            pizza = Pizza.query.get(new_restaurant_pizza.pizza_id)
            restaurant = Restaurant.query.get(new_restaurant_pizza.restaurant_id)
            return make_response(jsonify({
                "id": new_restaurant_pizza.id,
                "price": new_restaurant_pizza.price,
                "pizza_id": new_restaurant_pizza.pizza_id,
                "restaurant_id": new_restaurant_pizza.restaurant_id,
                "pizza": {
                    "id": pizza.id,
                    "name": pizza.name,
                    "ingredients": pizza.ingredients
                },
                "restaurant": {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address
                }
            }), 201)
        except ValueError as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)