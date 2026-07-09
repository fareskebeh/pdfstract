from flask import jsonify, render_template, request, redirect, make_response, url_for, flash
from .models import User
from db.extensions import db
import re
import random
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from payments.models import Plan
from keymanager.models import ApiKey

def generate_code():
    return random.randint(0000000, 9999999)

def auth_routes_init(app):
    @app.route("/home", methods=["GET"])
    def home():
        is_authenticated = True if session.get("email") else False
        return render_template("home.jinja", is_authenticated=is_authenticated)
    
    @app.route("/", methods=["GET"])
    def index():
        return redirect("/home")
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        is_authenticated = True if session.get("email") else False
        if is_authenticated:
            return redirect("/home")
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            if email:
                email_valid = re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
                if email_valid:
                    user = User.query.filter_by(email=email).first()
                    if user:
                        if user.is_verified:
                            flash("User already exists, please log in", "error")
                            return redirect("/login")
                        else:
                            code = generate_code()
                            print(f"CODE HAS BEEN SENT {email} \nDEBUG: {code}")
                            session['pending_verification_email'] = email
                            session['pending_verification_code'] = code
                            return redirect("/verify")
                    else:
                        user = User(email=email, password_hash=generate_password_hash(password))
                        db.session.add(user)
                        db.session.commit()
                        code = generate_code()
                        print(f"CODE HAS BEEN SENT {email} \nDEBUG: {code}")
                        session['pending_verification_email'] = email
                        session['pending_verification_code'] = code
                        return redirect("/verify")
                else:
                    flash("Invalid email format", "error")
            else:
                flash("Email is required", "error")
        
        return render_template('register.jinja', is_authenticated=is_authenticated)

    @app.route("/verify", methods=["GET", "POST"])
    def verify_email():
        email = session.get("pending_verification_email")
        if not email:
            flash("No verification in progress", "error")
            return redirect("/register")
        
        if request.method == "POST":
            code_user = str(request.form.get("code"))
            code_db = str(session.get("pending_verification_code"))

            print(f"DEBUG: code_user={code_user}, code_db={code_db}")
            
            if code_user == code_db:
                user = User.query.filter_by(email=email).first()
                if user:
                    user.is_verified = True
                    db.session.commit()
                    session.pop('pending_verification_email', None)
                    session.pop('pending_verification_code', None)
                    flash("Email verified! Please log in.", "success")
                    return redirect("/login")
                else:
                    flash("User not found", "error")
                    return redirect("/register")
            else:
                flash("Invalid verification code", "error")
        
        return render_template("verify.jinja", is_authenticated=True if email else False)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        is_authenticated = True if session.get("email") else False
        if is_authenticated:
            return redirect("/home")
        
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash("Invalid email/password", "error")
                return render_template('login.jinja', is_authenticated=is_authenticated)
            
            if not user.is_verified:
                code = generate_code()
                print(f"CODE HAS BEEN SENT {email} \nDEBUG: {code}")
                session['pending_verification_email'] = email
                session['pending_verification_code'] = code
                flash("Please verify your email first", "warning")
                return redirect("/verify")
            
            if check_password_hash(user.password_hash, password):
                session['email'] = email
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                flash("Invalid email/password", "error")
        
        return render_template('login.jinja', is_authenticated=is_authenticated)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))
    
    @app.route('/dashboard')
    def dashboard():
        is_authenticated = True if session.get("email") else False
        if not is_authenticated:
            flash("Please log in first", "warning")
            return redirect("/login")
        user = User.query.filter(User.email==session.get("email")).first()
        user_keys = ApiKey.query.filter(ApiKey.user_id==user.id)
        return render_template("dashboard.jinja", is_authenticated=is_authenticated, email=session.get("email"), user_keys=user_keys, user=user)

    @app.route('/pricing')
    def pricing():
        is_authenticated = True if session.get("email") else False
        plans = Plan.query.all() or []
        return render_template("pricing.jinja", plans=plans, is_authenticated=is_authenticated)