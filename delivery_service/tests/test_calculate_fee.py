import pytest

from delivery_service.tests.config import DeliveryService


def test_calculate_fee_successful():
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 200


@pytest.mark.parametrize("value", ["1", "!", 1.5, []])
def test_calculate_fee_not_successful_wrong_data_types_cart_value(value, key):
    data = {"cart_value": value, "delivery_distance": 1000, "number_of_items": 3, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 400
    assert "Validation error" in r.json()["message"]


@pytest.mark.parametrize("value", ["1", "!", 1.5, []])
def test_calculate_fee_not_successful_wrong_data_types_delivery_distance(value):
    data = {"cart_value": 1000, "delivery_distance": value, "number_of_items": 3, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 400
    assert "Validation error" in r.json()["message"]


@pytest.mark.parametrize("value", ["1", "!", 1.5, []])
def test_calculate_fee_not_successful_wrong_data_types_items(value):
    data = {"cart_value": 1000, "delivery_distance": 1000, "number_of_items": value, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 400
    assert "Validation error" in r.json()["message"]


@pytest.mark.parametrize("value", ["1", "!", 1.5, []])
def test_calculate_fee_not_successful_wrong_data_types_items(value):
    data = {"cart_value": 1000, "delivery_distance": 1000, "number_of_items": value, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    assert r.status_code == 400
    assert "Validation error" in r.json()["message"]