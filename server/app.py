#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods = ['GET'])
def get_restaurants():
    restaurants=Restaurant.query.all()
    restaurant_list=[restaurant.to_dict() for restaurant in restaurants]
    return jsonify(restaurant_list), 200

@app.route("/restaurants/<int:id>", methods = ['GET'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        restaurant_dict = restaurant.to_dict()
        pizzas = [
            {
            "id": restaurant_pizza.id,
            "pizza": {
                "id": restaurant_pizza.pizza.id,
                "name": restaurant_pizza.pizza.name,
                "ingredients": restaurant_pizza.pizza.ingredients
            },
            "pizza_id": restaurant_pizza.pizza_id,
            "price": restaurant_pizza.price,
            "restaurant_id": restaurant_pizza.restaurant_id
            }
        for restaurant_pizza in restaurant.restaurant_pizza
            ]
        restaurant_dict['restaurant_pizzas'] = pizzas
        return jsonify(restaurant_dict)
    else:
            response_data = {"error": "Restaurant not found"}
            return make_response(jsonify(response_data), 404)    
    
@app.route("/restaurants/<int:id>", methods = ['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        response_data = make_response(jsonify({"error": "Restaurant not found"}), 404)
    else: 
        db.session.delete(restaurant)
        db.session.commit()
        response_data = make_response(jsonify({"message": "Restaurant has been deleted!"}), 204)
    return response_data

@app.route("/pizzas", methods = ['GET'])
def get_pizzas():
    pizzas=Pizza.query.all()
    pizza_list=[pizza.to_dict() for pizza in pizzas]
    return jsonify(pizza_list), 200

@app.route("/restaurant_pizzas", methods = ['POST'])
def post_restaurant_pizzas():
    try:
        data = request.get_json()

        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if price not in range(1, 31):
            return jsonify({"errors": ['validation errors']}), 400

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        response_data = {
            "id": restaurant_pizza.id,
            "pizza": pizza.to_dict(),  
            "pizza_id": pizza.id,
            "price": price,
            "restaurant": restaurant.to_dict(),
            "restaurant_id": restaurant.id
        }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400
    finally:
        db.session.close()
  
if __name__ == "__main__":
    app.run(port=5555, debug=True)
