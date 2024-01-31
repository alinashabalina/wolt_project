from copy import deepcopy

import pytest

from delivery_service.tests.config import DeliveryService


def test_calculate_fee_successful(create_data_body):
    data = deepcopy(create_data_body)
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 710


def test_calculate_fee_successful_long_distance(create_data_body):
    data = deepcopy(create_data_body)
    data["delivery_distance"] = 23000000
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 1500


def test_calculate_fee_successful_friday_no_rush(create_data_body):
    data = deepcopy(create_data_body)
    data["time"] = "2024-01-19T13:00:00Z"
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 710


def test_calculate_fee_successful_friday_rush(create_data_body):
    data = deepcopy(create_data_body)
    data["time"] = "2024-01-19T16:00:00Z"
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 852


def test_calculate_fee_successful_many_items(create_data_body):
    data = deepcopy(create_data_body)
    data["number_of_items"] = 10000000
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 1500


def test_calculate_fee_successful_cart_value_free(create_data_body):
    data = deepcopy(create_data_body)
    data["cart_value"] = 20000000
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200
    assert r.json()["delivery_fee"] == 0


@pytest.mark.parametrize("val", ["1", "!", 1.5, [], {}])
def test_calculate_fee_not_successful_wrong_data_types_cart_value(val, create_data_body):
    data = deepcopy(create_data_body)
    for key, value in data.items():
        data[key] = val
        r = DeliveryService().calculate_fee(data=data)

        assert r.status_code == 400
        assert "Validation error" in r.json()["message"]


@pytest.mark.parametrize("key", ["cart_value", "delivery_distance", "number_of_items", "time"])
def test_calculate_fee_not_successful_missing_data(create_data_body, key):
    data = deepcopy(create_data_body)
    data.pop(key)
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 400
    assert "Validation error" in r.json()["message"]
