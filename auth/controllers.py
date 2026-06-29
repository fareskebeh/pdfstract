from flask import jsonify, render_template, request, redirect, make_response, url_for
from .models import User
from db.extensions import db
import re
import random
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

    
def generate_code():
    return random.randint(0000000, 9999999)

def auth_routes_init(app):
    @app.route("/home", methods=["GET"])
    def home():
        is_authenticated= True if session.get("email") else False
        return render_template("home.jinja", is_authenticated=is_authenticated)
    @app.route("/", methods=["GET"])
    def index():
        return redirect("/home")
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        is_authenticated= True if session.get("email") else False
        if is_authenticated:
            return redirect("/home")
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            if email:
                email_valid = re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
                if email_valid:
                    user= User.query.filter_by(email=email).first()
                    if user:
                        if user.is_verified:
                            return jsonify({"message":"User already exists, please log in"})
                        else:
                            code=generate_code()
                            print(f"CODE HAS BEEN SENT {email} \nDEBUG: {code}")
                            session['pending_verification_email']=email
                            session['pending_verification_code']=code
                            return redirect("/verify")
                    else:
                        user= User(email=email, password_hash=generate_password_hash(password))
                        db.session.add(user)
                        db.session.commit()
                        code=generate_code()
                        print(f"CODE HAS BEEN SENT {email} \nDEBUG: {code}")
                        session['pending_verification_email']=email
                        session['pending_verification_code']=code
                       
                        return redirect("/verify")
        return render_template('register.jinja')

    @app.route("/verify", methods=["GET", "POST"])
    def verify_email():
        email=session.get("pending_verification_email")
        if not email:
            return redirect("/home")
        if request.method =="POST":
            code_user=str(request.form.get("code"))
            code_db = str(session.get("pending_verification_code"))

            print(f"DEBUG: code_user={code_user}, code_db={code_db}") 
            if code_user == code_db:
                user = User.query.filter_by(email=email).first()
                if user:
                    user.is_verified = True
                    db.session.commit()
                    session.pop('pending_verification_email', None)
                    session.pop('pending_verification_code', None)
                    return redirect("/login")
            else:
                return jsonify({"error":"wrong code"})
        return render_template("verify.jinja")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        is_authenticated= True if session.get("email") else False
        if is_authenticated:
            return redirect("/home")
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user= User.query.filter_by(email=email).first()
            if user and user.email == email and check_password_hash(user.password_hash, password):
                session['email'] = email
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                return jsonify({"error": "Invalid email/password"})

        return render_template('login.jinja')
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))
    
    @app.route('/dashboard')
    def dashboard():
        is_authenticated= True if session.get("email") else False
        if not is_authenticated:
            return redirect("/home")
        return render_template("dashboard.jinja", is_authenticated=is_authenticated)