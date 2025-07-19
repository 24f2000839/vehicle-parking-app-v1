from models import db 
from sqlalchemy import UniqueConstraint 

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False) 
    spot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)

    parking_lot = db.relationship('ParkingLot', backref='spots', lazy=True)

    __table_args__ = (UniqueConstraint('lot_id', 'spot_number', name='_lot_spot_uc'),) 

    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} in Lot {self.lot_id} - Status: {self.status}>'
