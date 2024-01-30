from delivery_service.tests.config import DeliveryService


def test_calculate_fee():
    data = {"cart_value": 1, "delivery_distance": 2600, "number_of_items": 99, "time": "2024-01-26T13:00:00Z"}
    r = DeliveryService().calculate_fee(data=data)

    print(r.json())

