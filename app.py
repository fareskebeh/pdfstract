from flask import Flask
from dotenv import load_dotenv
import os
from core.controllers import register_routes
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
db = SQLAlchemy(app)
from auth.models import User

migrate = Migrate(app, db)


register_routes(app)

DEBUG=True if os.getenv("DEBUG") == 'True' else False
if __name__ == "__main__":
    app.run(debug=DEBUG, port=8000)