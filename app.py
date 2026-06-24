from flask import Flask
from dotenv import load_dotenv
import os
from core.controllers import core_routes_init
from auth.controllers import auth_routes_init
from ui.routes import ui_routes_init
from flask_migrate import Migrate
from db.extensions import db

load_dotenv()

app = Flask(__name__, template_folder="ui/templates")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
db.init_app(app)
from auth.models import User

migrate = Migrate(app, db)


core_routes_init(app)
auth_routes_init(app)
ui_routes_init(app)

DEBUG=True if os.getenv("DEBUG") == 'True' else False
if __name__ == "__main__":
    app.run(debug=DEBUG, port=8000)