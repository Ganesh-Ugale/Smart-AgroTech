import json
import os
from flask import Flask, request, jsonify
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")  # Replace for production

# Firebase Admin SDK setup
firebase_json = os.environ.get("FIREBASE_CREDENTIALS")

if not firebase_json:
    raise Exception("FIREBASE_CREDENTIALS environment variable is not set!")

cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)

# Basic route
@app.route('/')
def index():
    return jsonify({"message": "Flask app with Firebase is working!"})

# Example: Add user data to Firestore
@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing name field'}), 400

    doc_ref = db.collection('users').add({'name': data['name']})
    return jsonify({'message': 'User added', 'doc_id': doc_ref[1].id})

# Run app (not used in production with gunicorn)
if __name__ == '__main__':
    app.run(debug=True)
