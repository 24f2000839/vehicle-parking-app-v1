from flask import Flask, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from controllers.auth import auth_bp
from controllers.admin_routes import admin_bp
from controllers.user_routes import user_bp

from models import db
from models.user import User 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SHRUTI'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

@app.context_processor
def inject_user_status():
    current_user = None
    user_id = session.get('user_id')
    is_admin = session.get('logged_in_as') == 'admin'
    if user_id:
        current_user = User.query.get(user_id)
    else:
        current_user = None
    return dict(current_user=current_user, is_admin=is_admin)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logged_in_as', None)
    flash('You have been logged out.', 'info')
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin', email='admin@parkingapp.com', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user 'admin' created.")

    app.run(debug=True, port=4000)
