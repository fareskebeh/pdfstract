from flask import render_template, redirect

def ui_routes_init(app):
    @app.route("/", methods=["GET"])
    def index():
        return redirect('/home')
    
    @app.route("/home", methods=["GET"])
    def home():
        return render_template('home.jinja')
    
    @app.route("/register", methods=["GET"])
    def register_page():
        return render_template('register.jinja')
    @app.route("/login", methods=["GET"])
    def login_page():
        return render_template('login.jinja')