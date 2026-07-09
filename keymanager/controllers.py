from db.extensions import db
from auth.models import User
from flask import session, jsonify, request, render_template, flash, redirect
from .models import ApiKey
from hashlib import sha256
import secrets
import nemony as nm

def key_routes_init(app):
    
    @app.route("/count/<int:user_id>")
    def count_keys_for_user(user_id):
        user = User.query.get(user_id)
        if user is None:
            return {"error": "User not found"}, 404
        return str(user.key_count)
    
    @app.route("/keys/create", methods=["POST", "GET"])
    def create_key():
        is_authenticated=True if session.get("email") else False 
        if not is_authenticated:
            return jsonify({"message": "Unable to create key, requires authentication"})
        user = User.query.filter(User.email==session.get("email")).first()
        new_keys_available= True if (user.plan_id == 1 and user.key_count <1) or (user.plan_id == 2 and user.key_count <=3) else False
        raw=None
        if user and new_keys_available:

            raw=secrets.token_urlsafe(32)
            key = ApiKey(
                key_hash= sha256(raw.encode()).hexdigest(),
                name=nm.encode(raw, sep='-'),
                user_id=user.id,
            )
            db.session.add(key)
            db.session.commit()
            return render_template('create_key.jinja', name=key.name if key else '', raw=raw, is_authenticated=is_authenticated)
        else:
            flash('You have reached your API key limit for your current plan.')
            return redirect('/')