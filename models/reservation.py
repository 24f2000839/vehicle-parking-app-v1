from models import db
from datetime import datetime

from .user import User
from .parking_spot import ParkingSpot

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    license_plate = db.Column(db.String(20), nullable=False)
    vehicle_make_model = db.Column(db.String(50), nullable=True)

    user_obj = db.relationship('User', backref='reservations', lazy=True)
    parking_spot = db.relationship('ParkingSpot', backref='reservations', lazy=True)


    def __repr__(self):
        return f'<Reservation {self.id} | User: {self.user_id} | Spot: {self.spot_id} | Plate: {self.license_plate}>'

