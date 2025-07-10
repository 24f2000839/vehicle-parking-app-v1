from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from models.user import User
from datetime import datetime
from sqlalchemy.orm import joinedload # For efficient querying
from functools import wraps

user_bp = Blueprint('user', __name__)

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in_as') != 'user' or not session.get('user_id'):
            flash('Access denied. Please log in as a user.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@user_required
def user_dashboard():
    user_id = session['user_id']
    active_reservations = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).all()
    past_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp.isnot(None)
    ).order_by(Reservation.leaving_timestamp.desc()).all()

    total_cost_past = sum(r.parking_cost for r in past_reservations if r.parking_cost is not None)
    num_past_reservations = len(past_reservations)

    return render_template('user_dashboard.html',
                           active_reservations=active_reservations,
                           past_reservations=past_reservations,
                           total_cost_past=total_cost_past,
                           num_past_reservations=num_past_reservations)

@user_bp.route('/available_lots')
@user_required
def available_lots():
    available_parking_lots = ParkingLot.query.join(ParkingSpot).filter(ParkingSpot.status == 'A').distinct().all()

    user_id = session['user_id']
    past_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp.isnot(None)
    ).all()
    total_cost_past = sum(r.parking_cost for r in past_reservations if r.parking_cost is not None)
    num_past_reservations = len(past_reservations)


    return render_template('available_lots_user.html',
                           parking_lots=available_parking_lots,
                           total_cost_past=total_cost_past,
                           num_past_reservations=num_past_reservations)

@user_bp.route('/book_spot/<int:lot_id>', methods=['POST'])
@user_required
def book_spot(lot_id):
    user_id = session['user_id']
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    existing_reservation = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
    if existing_reservation:
        flash('You already have an active reservation. Please release it before booking a new one.', 'warning')
        return redirect(url_for('user.user_dashboard'))

    license_plate = request.form['license_plate'].strip().upper()
    vehicle_make_model = request.form.get('vehicle_make_model', '').strip()

    if not license_plate:
        flash('License plate is required to book a spot.', 'danger')
        return redirect(url_for('user.available_lots'))

    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if available_spot:
        available_spot.status = 'O'
        db.session.add(available_spot)

        new_reservation = Reservation(
            spot_id=available_spot.id,
            user_id=user_id,
            parking_timestamp=datetime.utcnow(), # Records current time
            license_plate=license_plate, # Save license plate
            vehicle_make_model=vehicle_make_model # Save vehicle make/model
        )
        db.session.add(new_reservation)
        db.session.commit()
        flash(f'Spot {available_spot.spot_number} in Lot {available_spot.parking_lot.prime_location_name} booked successfully for vehicle {license_plate}!', 'success')
        return redirect(url_for('user.user_dashboard'))
    else:
        flash('No available spots in this parking lot at the moment. Please try another lot.', 'danger')
        return redirect(url_for('user.available_lots'))

@user_bp.route('/release_spot/<int:reservation_id>', methods=['POST'])
@user_required
def release_spot(reservation_id):
    user_id = session['user_id']
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id, leaving_timestamp=None).first()

    if not reservation:
        flash('Active reservation not found or already released.', 'danger')
        return redirect(url_for('user.user_dashboard'))

    reservation.leaving_timestamp = datetime.utcnow()

    parking_spot = reservation.parking_spot
    parking_lot = parking_spot.parking_lot

    if duration_hours < 1 and duration_hours > 0:
        actual_charge_hours = 1.0 # Minimum 1 hour charge
    else:
        actual_charge_hours = duration_hours # Charge based on actual hours

    reservation.parking_cost = actual_charge_hours * parking_lot.price_per_hour
    db.session.add(reservation)

    parking_spot.status = 'A'
    db.session.add(parking_spot)

    db.session.commit()
    flash(f'Spot released. Total cost: ${reservation.parking_cost}. Duration: {duration_hours} hours.', 'success')
    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/summary_charts')
@user_required
def user_summary_charts():
    flash('This is a placeholder for user summary charts. Implement charting logic here.', 'info')
    return redirect(url_for('user.user_dashboard')) # Redirect or render a specific chart page

