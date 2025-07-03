from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .parking_lot import ParkingLot
from .parking_spot import ParkingSpot
from .reservation import Reservation

