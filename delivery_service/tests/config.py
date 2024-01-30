import requests


class DeliveryService:
    url = "http://127.0.0.1:5000"
    delivery_fee_endpoint = "/calculate"

    def __init__(self):
        pass

    def calculate_fee(self, data):
        response = requests.post(self.url + self.delivery_fee_endpoint, json=data)
        return response
