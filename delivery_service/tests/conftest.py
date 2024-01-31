import pytest

from delivery_service.tests.config import DeliveryService


@pytest.fixture(autouse=True)
def service_availability():
    service = DeliveryService().check_service()
    if service.status_code != 200:
        raise Exception(f"Service is not available : status code {service.status_code}")


@pytest.fixture()
def create_data_body():
    data = {
        "cart_value": 790,
        "delivery_distance": 2235,
        "number_of_items": 4,
        "time": "2024-01-15T13:00:00Z"
    }

    return data
