from flask import Flask, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

from models import db
from models.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shruti123' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logged_in_as', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='password', email='admin@parkingapp.com', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user 'admin' created. Password is 'password' (hardcoded for demo).")

    app.run(debug=True, port=4000)
