# routes.py
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import User, db  # Import User model and database
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Meme

routes = Blueprint('routes', __name__)

app = Flask(__name__)

@app.route('/toggle_follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow in current_user.following:
        current_user.following.remove(user_to_follow)
        following_status = "Follow +"
    else:
        current_user.following.append(user_to_follow)
        following_status = "Following"
    db.session.commit()
    return jsonify({"status": following_status})


@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if user and user != current_user:
        current_user.follow(user)
        db.session.commit()
        return jsonify({"status": "followed"})
    return jsonify({"error": "Cannot follow this user"}), 400

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if user and user != current_user:
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({"status": "unfollowed"})
    return jsonify({"error": "Cannot unfollow this user"}), 400
