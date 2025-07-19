from models import db

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False, unique=True)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    pin_code = db.Column(db.String(10), nullable=True)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name} (ID: {self.id})>'

