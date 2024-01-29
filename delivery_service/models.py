from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.app = app
    db.init_app(app)


class DeliveryFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_fee = db.Column(db.Integer, unique=False)

    def delivery_info(self):
        return {
            "id": self.id,
            "delivery_fee": self.delivery_fee
        }
