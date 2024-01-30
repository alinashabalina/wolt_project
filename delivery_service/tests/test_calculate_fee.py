from delivery_service.tests.config import DeliveryService


def test_calculate_fee():
    data = {"cart_value": 1, "delivery_distance": 1, "number_of_items": 1, "time": "2021-12-31T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    print(r.json())

