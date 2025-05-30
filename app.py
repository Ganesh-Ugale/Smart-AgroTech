from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'smartagro_secret_key'

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-service-account.json')  # Rename if needed
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize SQLite DB for user auth
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        email TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = user[1]  # Store name
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, mobile, email, password) VALUES (?, ?, ?, ?)",
                      (name, mobile, email, password))
            conn.commit()
            conn.close()

            # Also save to Firestore 'user' collection
            user_data = {
                'name': name,
                'mobile': mobile,
                'email': email,
            }
            db.collection('user').add(user_data)

            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Email already registered')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/soil_testing')
def soil_testing():
    if 'user' not in session:
        return redirect(url_for('login'))

    sensor_data = {
        'temperature': '29°C',
        'pH': '6.5',
        'moisture': '42%',
        'crop_prediction': ['Wheat', 'Barley', 'Millet']
    }

    # Save to Firestore in 'soil_tests' collection
    soil_test_data = {
        'user': session['user'],
        'temperature': sensor_data['temperature'],
        'pH': sensor_data['pH'],
        'moisture': sensor_data['moisture'],
        'predicted_crops': sensor_data['crop_prediction'],
        'status': 'Tested'
    }
    db.collection('soil_tests').add(soil_test_data)

    return render_template('soil_testing.html', sensor_data=sensor_data, user=session['user'])

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('about.html', user=session['user'])

@app.route('/contact')
def contact():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
