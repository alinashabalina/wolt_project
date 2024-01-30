import json
from copy import deepcopy
from datetime import datetime

import jsonschema
from dateutil import parser
from flask import Flask, jsonify, request
from flask_migrate import Migrate

from models import init_app, db, DeliveryFee
from schemas import DeliverySchema

app = Flask(__name__)

app.config['SECRET_KEY'] = "key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/delivery_fee.db'
init_app(app)
migrate = Migrate(app, db)


def _check_free(data):
    return data["cart_value"] >= 20000


def _check_cart_value(data):
    fee = 0
    if data["cart_value"] < 1000:
        fee = 1000 - data["cart_value"]
        return fee
    else:
        return fee


def _check_distance(data):
    if data["delivery_distance"] <= 1000:
        fee = 200
        return fee
    else:
        d = deepcopy(data["delivery_distance"])
        fee = 200
        while d > 1000:
            fee += 100
            d -= 500
        return fee


def _check_items(data):
    fee = 0
    if data["number_of_items"] <= 4:
        fee = 0
        return fee
    elif (data["number_of_items"] > 4) and (data["number_of_items"] <= 12):
        fee = (data["number_of_items"] - 4) * 50
        return fee
    elif data["number_of_items"] > 12:
        fee = (data["number_of_items"] - 4) * 50 + 120
        return fee
    else:
        return fee


def _check_friday(data):
    if datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%SZ").isoweekday() != 5:
        return False
    else:
        return True


def _check_time(data):
    request_time = parser.parse(data["time"])
    if 15 <= request_time.hour <= 19:
        return True
    else:
        return False


@app.route("/calculate", methods=['POST'])
def calculate_fee():
    try:
        fee = DeliveryFee()
        jsonschema.validate(instance=json.loads(request.data), schema=DeliverySchema.DeliveryFee)
        fee_sum = 0
        data = json.loads(request.data)
        if _check_free(data=json.loads(request.data)) is False:
            fee_sum = _check_cart_value(data=data) + _check_items(data=data) + _check_distance(data=data)
            if _check_friday(data=data) is True and _check_time(data=data) is True:
                fee_sum *= 1.2
            if fee_sum > 1500:
                fee_sum = 1500
        fee.delivery_fee = fee_sum
        db.session.add(fee)
        db.session.commit()
        return jsonify({"delivery_fee": fee_sum}), 200
    except jsonschema.exceptions.ValidationError as e:
        db.session.rollback()
        response = {
            "message": f"Validation error: {e.message}",

        }
        return jsonify(response), 400

    except ValueError as e:
        db.session.rollback()
        response = {
            "message": f"Validation error: {e}",

        }
        return jsonify(response), 400
