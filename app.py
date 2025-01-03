from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management and flash messages

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the user table if it does not exist (will happen only once, or after the DB file is deleted)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            logged_in INTEGER NOT NULL,
            GeverPoints INTEGER NOT NULL,
            GiverPoints INTEGER NOT NULL,
            last_active TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Make sure everyone is logged out when the server starts
    cursor.execute('UPDATE users SET logged_in = 0 WHERE logged_in = 1')
    conn.commit()

    conn.close()

def update_giver_points():
    while True:
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET GiverPoints = GiverPoints + 10 WHERE logged_in = 1')
        conn.commit()
        conn.close()

# @app.before_request
# def check_inactivity():
#     username = session.get('username')
#     if username:
#         conn = sqlite3.connect('users.db')
#         cursor = conn.cursor()
#         cursor.execute('SELECT last_active FROM users WHERE username = ?', (username,))
#         last_active = cursor.fetchone()[0]
#         conn.close()

#         # Define the local timezone (e.g., 'Asia/Jerusalem' for GMT+2)
#         local_timezone = pytz.timezone('Asia/Jerusalem')
#         naive_datetime = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S')
#         aware_datetime = naive_datetime.replace(tzinfo=local_timezone)

    # does not work for some reason; disabled for now.     
        # print("aware_datetime=", aware_datetime)
        # print("datetime.now=", datetime.now(local_timezone))
        # print("datetime - 125", datetime.now(local_timezone) - timedelta(minutes=125))

        # if aware_datetime < (datetime.now(local_timezone) - timedelta(minutes=5)):
        #     print("logging out")
        #     logout_user()

def logout_user():
    username = session.get('username')
    if username:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET logged_in = 0 WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        session.pop('username', None)
        flash('Logged out due to inactivity.', 'warning')

@app.route('/')
def home_redirect():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    username = session.get('username')
    if username:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?', (username,))
        conn.commit()
        cursor.execute('SELECT GeverPoints, GiverPoints FROM users WHERE username = ?', (username,))
        user_points = cursor.fetchone()
        conn.close()
        if user_points:
            gever_points, giver_points = user_points
            return render_template('home.html', username=username, gever_points=gever_points, giver_points=giver_points)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            if user[2] == password:
                session['username'] = username
                cursor.execute('UPDATE users SET logged_in = 1, last_active = CURRENT_TIMESTAMP WHERE username = ?', (username,))
                conn.commit()
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
        else:
            cursor.execute('''
                INSERT INTO users (username, password, logged_in, GeverPoints, GiverPoints, last_active)
                VALUES (?, ?, 1, 0, 10, CURRENT_TIMESTAMP)
            ''', (username, password))
            session['username'] = username
            conn.commit()
            flash('New user created and logged in!', 'success')
            return redirect(url_for('home'))

        conn.close()
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return '''
    <h1>Welcome to the dashboard!</h1>
    <a href="/logout">Logout</a>
    '''

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET logged_in = 0 WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        session.pop('username', None)
        flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/givepoints', methods=['GET', 'POST'])
def givepoints():
    username = session.get('username')
    if request.method == 'POST':
        recipient = request.form['recipient']
        points_to_give = int(request.form['points'])

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT GiverPoints FROM users WHERE username = ?', (username,))
        user_giver_points = cursor.fetchone()[0]

        if user_giver_points >= points_to_give:
            cursor.execute('UPDATE users SET GiverPoints = GiverPoints - ? WHERE username = ?', (points_to_give, username))
            cursor.execute('UPDATE users SET GeverPoints = GeverPoints + ? WHERE username = ?', (points_to_give, recipient))
            conn.commit()
            flash(f'{points_to_give} points given to {recipient}!', 'success')
        else:
            flash('Insufficient points to give.', 'error')
        
        conn.close()
        return redirect(url_for('home'))
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, GeverPoints FROM users')
        users = cursor.fetchall()
        conn.close()
        return render_template('givepoints.html', users=users)


if __name__ == '__main__':
    init_db()
    background_thread = threading.Thread(target=update_giver_points)
    background_thread.daemon = True
    background_thread.start()
    app.run(debug=True)
