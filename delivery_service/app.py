import json
import math
from copy import deepcopy
from datetime import datetime

import jsonschema
from dateutil import parser
from flask import Flask, jsonify, request
from flask_migrate import Migrate

from models import init_app, db
from schemas import DeliverySchema

app = Flask(__name__)

app.config['SECRET_KEY'] = "key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/delivery_fee.db'
init_app(app)
migrate = Migrate(app, db)


def _check_free(data):
    fee = 0
    if data["cart_value"] >= 20000:
        return fee
    else:
        return False


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


def _check_d(data):
    distance_units = data["delivery_distance"] / 500
    distance_units = max(math.ceil(distance_units), 2)
    return 1 * distance_units


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
    fee_rate = 1
    if datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%SZ").isoweekday() != 5:
        return False, fee_rate
    else:
        return True, fee_rate


def _check_time(data):
    request_time = parser.parse(data["time"])
    if (int(str(datetime.time(request_time))[:2]) >= 15) and (int(str(datetime.time(request_time))[:2]) <= 19):
        return True
    else:
        return False


@app.route("/calculate", methods=['POST'])
def calculate_fee():
    try:
        jsonschema.validate(instance=json.loads(request.data), schema=DeliverySchema.DeliveryFee)
        fee_sum = 0
        data = json.loads(request.data)
        if _check_free(data=json.loads(request.data)) is False:
            fee_sum = _check_cart_value(data=data) + _check_items(data=data) + _check_distance(data=data)
            if fee_sum > 1500:
                fee_final = 1500
                if _check_friday(data=data)[0] is False:
                    fee_final = fee_final
                return jsonify({"delivery_fee": fee_final}), 200
            else:
                if _check_time(data=data) is True:
                    fee_sum = (_check_cart_value(data=data) + _check_items(data=data) + _check_distance(data=data)) * 1.2
                    if fee_sum > 1500:
                        fee_final = 1500
                        return jsonify({"delivery_fee": fee_final}), 200
                else:
                    fee_sum = _check_cart_value(data=data) + _check_items(data=data) + _check_distance(data=data)
                    if fee_sum > 1500:
                        fee_final = 1500
                        return jsonify({"delivery_fee": fee_final}), 200
        else:
            return jsonify({"delivery_fee": fee_sum}), 200
    except jsonschema.exceptions.ValidationError as e:
        response = {
            "message": f"Validation error: {e.message}",

        }
        return jsonify(response), 400
