from models import db

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)
    parking_lot = db.relationship('ParkingLot', backref='spots', lazy=True)
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} in Lot {self.lot_id} - Status: {self.status}>'

