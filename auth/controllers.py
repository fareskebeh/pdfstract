from flask import jsonify, render_template, request, redirect, make_response, url_for
from .models import User
from db.extensions import db
import re
import random
from flask import session

    
def generate_code():
    return random.randint(0000000, 9999999)

def auth_routes_init(app):
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
                        user= User(email=email, password=password)
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
            return redirect("/")
        if request.method =="POST":
            code_user=request.form.get("code")
            code_db = session.get("pending_verification_code")

            print(f"DEBUG: code_user={code_user}, code_db={code_db}") 
            if code_user == code_db:
                user = User.query.filter_by(email=email).first()
                if user:
                    user.is_verified = True
                    user.verification_code = None
                    db.session.commit()
                    session.pop('pending_verification_email', None)
                    session.pop('pending_verification_code', None)
                    return redirect(url_for('login'))
        return render_template("verify.jinja")

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            

        return render_template('login.jinja')