from flask import jsonify, render_template, request, redirect, make_response, url_for
from .models import User
from db.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from functools import wraps


def auth_routes_init(app):
    print()
    @app.route("/home", methods=["GET"])
    def home():
        return render_template("home.jinja")
    @app.route("/", methods=["GET"])
    def index():
        return redirect("/home")
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'message': 'User already exists. Please login.'}), 400

            hashed_password = generate_password_hash(password)
            new_user = User(public_id=str(uuid.uuid4()), email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

        return render_template('register.jinja')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password, password):
                return jsonify({'message': 'Invalid email or password'}), 401

            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                            app.config['SECRET_KEY'], algorithm="HS256")

            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('jwt_token', token)

            return response

        return render_template('login.jinja')