import json
import math
import random
import string
from copy import deepcopy
from datetime import datetime
from functools import wraps

import jsonschema
import requests
import sqlalchemy
from flask import Flask, jsonify, request, redirect
from flask_migrate import Migrate
from sqlalchemy import select

from delivery_service.schemas import DeliverySchema
from models import init_app, db, DeliveryFee
app = Flask(__name__)

app.config['SECRET_KEY'] = "opop"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/delivery_fee.db'
init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def index_page():
    response = {"message": "This page is empty"}
    return jsonify(response), 200


def _check_free(data):
    if data["cart_value"] >= 20000:
        return True

def _check_cart_value(data):
    if data["cart_value"] < 1000:
        return True, 1000 - data["cart_value"]

def _check_distance(data):
    if data["delivery_distance"] <= 1000:
        fee = 2
    else:
        d = deepcopy(data["delivery_distance"])
        fee = 2
        while d > 1000:
            fee += 1
            d -= 500
    return True, fee

def _check_d(data):
    distance_units = data["delivery_distance"] / 500
    distance_units = max(math.ceil(distance_units), 2)
    return 1 * distance_units


def _check_items(data):
    if data["number_of_items"] <= 4:
        fee = 0
    elif (data["number_of_items"] > 4) and (data["number_of_items"] < 12):
        fee = (data["number_of_items"] - 4) * 50
    elif data["number_of_items"] > 12:
        fee =  (data["number_of_items"] - 4) * 50 + 120

    return True, fee

@app.route("/calculate", methods=['POST'])
def calculate_fee():
    fee = DeliveryFee()
    jsonschema.validate(instance=json.loads(request.data), schema=DeliverySchema.DeliveryFee)





