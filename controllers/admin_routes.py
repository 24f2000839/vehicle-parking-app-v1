from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.user import User
from models.reservation import Reservation
from sqlalchemy.orm import joinedload 

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def admin_dashboard():
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = total_spots - occupied_spots
    total_users = User.query.filter_by(is_admin=False).count() 

    chart_data = {
        'labels': ['Occupied', 'Available'],
        'data': [occupied_spots, available_spots]
    }

    return render_template('admin_dashboard.html',
                           total_lots=total_lots,
                           total_spots=total_spots,
                           occupied_spots=occupied_spots,
                           available_spots=available_spots,
                           total_users=total_users,
                           chart_data=chart_data)


@admin_bp.route('/create_parking_lot', methods=['GET', 'POST'])
def create_parking_lot():
    if request.method == 'POST':
        prime_location_name = request.form['prime_location_name']
        try:
            price_per_hour = float(request.form['price_per_hour'])
            maximum_number_of_spots = int(request.form['maximum_number_of_spots'])
        except ValueError:
            flash('Price per hour and maximum spots must be valid numbers.', 'danger')
            return redirect(url_for('admin.create_parking_lot'))

        address = request.form.get('address')
        pin_code = request.form.get('pin_code')

        if not prime_location_name or price_per_hour <= 0 or maximum_number_of_spots <= 0:
            flash('Please fill in all required fields and ensure values are positive.', 'danger')
            return redirect(url_for('admin.create_parking_lot'))

        if ParkingLot.query.filter_by(prime_location_name=prime_location_name).first():
            flash('A parking lot with this name already exists.', 'danger')
            return redirect(url_for('admin.create_parking_lot'))

        new_lot = ParkingLot(
            prime_location_name=prime_location_name,
            price_per_hour=price_per_hour,
            address=address,
            pin_code=pin_code,
            maximum_number_of_spots=maximum_number_of_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        for i in range(1, maximum_number_of_spots + 1):
            new_spot = ParkingSpot(
                lot_id=new_lot.id,
                spot_number=f'SP{i}',
                status='A'
            )
            db.session.add(new_spot)
        db.session.commit()
        flash(f'Parking Lot "{new_lot.prime_location_name}" created successfully with {maximum_number_of_spots} spots!', 'success')
        return redirect(url_for('admin.list_parking_lots'))
    return render_template('create_parking_lot.html')

@admin_bp.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        try:
            new_max_spots = int(request.form['maximum_number_of_spots'])
            price_per_hour = float(request.form['price_per_hour'])
        except ValueError:
            flash('Maximum spots and price must be valid numbers.', 'danger')
            return redirect(url_for('admin.edit_parking_lot', lot_id=lot.id))

        if new_max_spots < 0 or price_per_hour <= 0:
            flash('Maximum spots and price must be positive.', 'danger')
            return redirect(url_for('admin.edit_parking_lot', lot_id=lot.id))

        current_occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        if new_max_spots < current_occupied_spots:
            flash(f'Cannot reduce spots to {new_max_spots}. There are still {current_occupied_spots} occupied spots.', 'danger')
            return redirect(url_for('admin.edit_parking_lot', lot_id=lot.id))

        lot.prime_location_name = request.form['prime_location_name']
        lot.price_per_hour = price_per_hour
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')

        if new_max_spots > lot.maximum_number_of_spots:
            for i in range(lot.maximum_number_of_spots + 1, new_max_spots + 1):
                new_spot = ParkingSpot(lot_id=lot.id, spot_number=f'SP{i}', status='A')
                db.session.add(new_spot)
        elif new_max_spots < lot.maximum_number_of_spots:
            spots_to_delete = ParkingSpot.query.filter(
                ParkingSpot.lot_id == lot.id,
                ParkingSpot.spot_number.like(f'SP%'), 
                ParkingSpot.status == 'A' 
            ).order_by(ParkingSpot.id.desc()).limit(lot.maximum_number_of_spots - new_max_spots).all()

            if len(spots_to_delete) < (lot.maximum_number_of_spots - new_max_spots):
                 flash('Cannot reduce spots further, some spots are occupied.', 'danger')
                 return redirect(url_for('admin.edit_parking_lot', lot_id=lot.id))

            for spot in spots_to_delete:
                db.session.delete(spot)

        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        flash(f'Parking Lot "{lot.prime_location_name}" updated successfully!', 'success')
        return redirect(url_for('admin.list_parking_lots'))
    return render_template('edit_parking_lot.html', lot=lot)

@admin_bp.route('/delete_parking_lot/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

    if occupied_spots_count > 0:
        flash(f'Cannot delete parking lot "{lot.prime_location_name}". It still has {occupied_spots_count} occupied spots.', 'danger')
    else:
        db.session.delete(lot)
        db.session.commit()
        flash(f'Parking lot "{lot.prime_location_name}" and its spots deleted successfully.', 'success')
    return redirect(url_for('admin.list_parking_lots'))


@admin_bp.route('/parking_lots')
def list_parking_lots():
    parking_lots = ParkingLot.query.options(joinedload(ParkingLot.spots)).all()
    return render_template('list_parking_lots_admin.html', parking_lots=parking_lots)

@admin_bp.route('/users')
def list_users():
    users = User.query.filter_by(is_admin=False).all() 
    return render_template('list_users_admin.html', users=users)

@admin_bp.route('/summary_charts')
def admin_summary_charts():
    flash('This is a placeholder for admin summary charts. Implement charting logic here.', 'info')
    return render_template('admin_dashboard.html') 

