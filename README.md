# wolt_delivery_fee_project

This is a project aiming at calculating delivery fee based on several parameters: cost of the cart, distance, number of items and date/time.

The project is created with Python/Flask and tested with unittest/pytest.

All the necessary dependencies for running the project locally are stored in `requirements.txt`
To install all the dependencies for the project one has to run the following commands:

```
cd delivery_service
pip3 install -r requirements.txt
```

To create a database one has to run the following commands:

```
flask db init
flask db migrate
flask db upgrade
```

To run the project one has to run th following command in the delivery_service folder:

```
flask --app app run
```

To run tests one has to run the following commands from the delivery_service folder:

```
cd tests
pytest
```

Note that the app should be running on port 5000 (default for Flask) or the tests will throw an exception "Service not running"

