from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not username or not password or not email:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, password=password, email=email, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            session['logged_in_as'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['logged_in_as'] = 'user'
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('user.user_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

