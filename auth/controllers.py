from flask import jsonify
from .models import User
from db.extensions import db

def auth_routes_init(app):
    @app.route("/keys/create", methods=["POST"])
    def create_key():
        return jsonify({"text": "hold"})