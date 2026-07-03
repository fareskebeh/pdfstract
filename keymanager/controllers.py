from flask import request
from db.extensions import db
from auth.models import User


def key_routes_init(app):
    
    @app.route("/count/<int:user_id>")
    def count_keys_for_user(user_id):
        user = User.query.get(user_id)
        if user is None:
            return {"error": "User not found"}, 404
        return str(user.key_count)