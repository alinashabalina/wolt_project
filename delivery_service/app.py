import json
import unittest
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


def _check_free(data: dict) -> bool:
    return data["cart_value"] >= 20000


def _check_cart_value(data: dict) -> int:
    fee = 0
    if data["cart_value"] < 1000:
        fee = 1000 - data["cart_value"]
        return fee
    else:
        return fee


def _check_distance(data: dict) -> int:
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


def _check_items(data: dict) -> int:
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


def _check_friday(data: dict) -> bool:
    if datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%SZ").isoweekday() != 5:
        return False
    else:
        return True


def _check_time(data: dict) -> bool:
    request_time = parser.parse(data["time"])
    if 15 <= request_time.hour <= 19:
        return True
    else:
        return False


@app.route("/")
def index_page():
    response = {"message": "This page is empty"}
    return jsonify(response), 200


@app.route("/calculate", methods=['POST'])
def calculate_fee() -> json:
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


class CheckFreeTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_free_less(self):
        result = _check_free(self.data)
        self.assertFalse(result)

    def test_check_free_1_less(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 19999
        result = _check_free(data_new)
        self.assertFalse(result)

    def test_check_free_float(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 19999.99
        result = _check_free(data_new)
        self.assertFalse(result)

    def test_check_free_free_with_long_distance(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 20000
        data_new["delivery_distance"] = 2000000000000
        result = _check_free(data_new)
        self.assertTrue(result)

    def test_check_free_free(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 20000
        result = _check_free(data_new)
        self.assertTrue(result)

    def test_check_free_string(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = "20000"
        self.assertRaises(TypeError, _check_free(data_new))


class CheckCartValueTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_cart_value_surge(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 1
        result = _check_cart_value(data_new)
        self.assertEqual(result, 999)

    def test_check_cart_value_surge_999(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 999
        result = _check_cart_value(data_new)
        self.assertEqual(result, 1)

    def test_check_cart_value_no_surge_1000(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 1000
        result = _check_cart_value(data_new)
        self.assertEqual(result, 0)

    def test_check_cart_value_no_surge_more_than_1000(self):
        data_new = deepcopy(self.data)
        data_new["cart_value"] = 1001
        result = _check_cart_value(data_new)
        self.assertEqual(result, 0)


class CheckDistanceTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_delivery_distance_no_surge(self):
        data_new = deepcopy(self.data)
        data_new["delivery_distance"] = 999
        result = _check_distance(data_new)
        self.assertEqual(result, 200)

    def test_check_delivery_distance_no_surge_1000(self):
        data_new = deepcopy(self.data)
        data_new["delivery_distance"] = 1000
        result = _check_distance(data_new)
        self.assertEqual(result, 200)

    def test_check_delivery_distance_surge_1001(self):
        data_new = deepcopy(self.data)
        data_new["delivery_distance"] = 1001
        result = _check_distance(data_new)
        self.assertEqual(result, 300)

    def test_check_delivery_distance_surge_1501(self):
        data_new = deepcopy(self.data)
        data_new["delivery_distance"] = 1501
        result = _check_distance(data_new)
        self.assertEqual(result, 400)


class CheckItemsTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_items_no_surge(self):
        data_new = deepcopy(self.data)
        data_new["number_of_items"] = 4
        result = _check_items(data_new)
        self.assertEqual(result, 0)

    def test_check_items_surge(self):
        data_new = deepcopy(self.data)
        data_new["number_of_items"] = 7
        result = _check_items(data_new)
        self.assertEqual(result, 150)

    def test_check_items_surge_11(self):
        data_new = deepcopy(self.data)
        data_new["number_of_items"] = 11
        result = _check_items(data_new)
        self.assertEqual(result, 350)

    def test_check_items_surge_12(self):
        data_new = deepcopy(self.data)
        data_new["number_of_items"] = 12
        result = _check_items(data_new)
        self.assertEqual(result, 400)

    def test_check_items_surge_13(self):
        data_new = deepcopy(self.data)
        data_new["number_of_items"] = 13
        result = _check_items(data_new)
        self.assertEqual(result, 570)


class CheckFridayTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_friday_not_friday(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-01-25T13:00:00Z"
        result = _check_friday(data_new)
        self.assertFalse(result)

    def test_check_friday_not_friday_leap(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-02-29T13:00:00Z"
        result = _check_friday(data_new)
        self.assertFalse(result)

    def test_check_friday_friday_leap(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-03-01T13:00:00Z"
        result = _check_friday(data_new)
        self.assertTrue(result)


class CheckTimeTests(unittest.TestCase):
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}

    def test_check_time_not_friday_timerange(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-01-25T15:00:01Z"
        result = _check_time(data_new)
        self.assertTrue(result)

    def test_check_time_friday_timerange(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-01-18T15:00:00Z"
        result = _check_time(data_new)
        self.assertTrue(result)

    def test_check_time_friday_not_timerange(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-03-01T20:00:00Z"
        result = _check_time(data_new)
        self.assertFalse(result)

    def test_check_time_not_friday_not_timerange(self):
        data_new = deepcopy(self.data)
        data_new["time"] = "2024-02-29T14:59:59Z"
        result = _check_time(data_new)
        self.assertFalse(result)
