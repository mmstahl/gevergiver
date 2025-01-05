from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'users.db')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(16), nullable=False)
    gever_points = db.Column(db.Integer, default=0)
    giver_points = db.Column(db.Integer, default=100)
    signed_in = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def sign_in():
    return render_template('sign_in.html')

@app.route('/home')
def home():
    username = session.get('current_username')
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('home.html', username=user.username, gever_points=user.gever_points, giver_points=user.giver_points)
    return redirect(url_for('sign_in'))

@app.route('/players')
def players():
    current_username = session.get('current_username')
    current_user = User.query.filter_by(username=current_username).first()
    users = User.query.all()
    return render_template('players.html', users=users, current_username=current_username, current_user_giver_points=current_user.giver_points if current_user else 0)

@app.route('/sign_in', methods=['POST'])
def sign_in_post():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()

    if len(username) < 4 or len(password) < 4:
        flash('Username and password minimum length is 4 characters.')
        return redirect(url_for('sign_in'))
    if len(username) > 16 or len(password) > 16:
        flash('Username and password maximum length is 16 characters.')
        return redirect(url_for('sign_in'))
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            user.signed_in = True
            user.last_activity = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT-2'))
            db.session.commit()
            session['current_username'] = username
            return redirect(url_for('home'))
        else:
            flash('This username exists already, but the password is incorrect')
            return redirect(url_for('sign_in'))
    else:
        last_activity = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Etc/GMT-2'))
        new_user = User(username=username, password=password, signed_in=True, last_activity=last_activity)
        db.session.add(new_user)
        db.session.commit()
        session['current_username'] = username
        return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
def logout():
    username = session.get('current_username')
    user = User.query.filter_by(username=username).first()
    if user:
        user.signed_in = False
        db.session.commit()
    session.pop('current_username', None)
    return redirect(url_for('sign_in'))

@app.route('/transfer_points/<username>', methods=['GET', 'POST'])
def transfer_points(username):
    current_username = session.get('current_username')
    if request.method == 'POST':
        points = int(request.form.get('points'))
        current_user = User.query.filter_by(username=current_username).first()
        selected_user = User.query.filter_by(username=username).first()

        if current_user and selected_user and points <= current_user.giver_points:
            current_user.giver_points -= points
            selected_user.gever_points += points
            db.session.commit()
            flash('Points transferred successfully!')
            return redirect(url_for('home'))

    current_user = User.query.filter_by(username=current_username).first()
    return render_template('transfer_points.html', current_username=current_username, selected_username=username, current_user_giver_points=current_user.giver_points)

def update_giver_points():
    job_id = str(uuid.uuid4())
    print(f"Running job ID: {job_id} at {datetime.now()}")
    with app.app_context():
        signed_in_users = User.query.filter_by(signed_in=True).all()
        for user in signed_in_users:
            user.giver_points += 5
            db.session.commit()
    print(f"Completed job ID: {job_id} at {datetime.now()}")

def reset_signed_in_status():
    with app.app_context():
        users = User.query.all()
        for user in users:
            user.signed_in = False
        db.session.commit()

# Configure the scheduler
job_defaults = {
    'coalesce': True,
    'max_instances': 1
}
scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(1)}, job_defaults=job_defaults)
scheduler.add_job(update_giver_points, 'interval', seconds=10)
scheduler.start()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        reset_signed_in_status()
    app.run(debug=True)
