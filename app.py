from flask import Flask
from dotenv import load_dotenv
import os
from core.controllers import core_routes_init
from auth.controllers import auth_routes_init
from keymanager.controllers import key_routes_init
from flask_migrate import Migrate
from db.extensions import db
from auth.models import User
from keymanager.models import ApiKey
from payments.models import Plan

load_dotenv()

app = Flask(__name__, template_folder="auth/templates")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
app.config["REMEMBER_COOKIE_SAMESITE"] = os.getenv("REMEMBER_COOKIE_SAMESITE")
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db.init_app(app)

migrate = Migrate(app, db)


core_routes_init(app)
auth_routes_init(app)
key_routes_init(app)

DEBUG=True if os.getenv("DEBUG") == 'True' else False
if __name__ == "__main__":
    app.run('0.0.0.0',debug=DEBUG, port=8000)