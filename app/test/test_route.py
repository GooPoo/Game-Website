from flask import Blueprint, jsonify
from app import db
from app.models import User

@test_bp.route('/test_query')
def test_query():
    try:
        # Attempt to query all users
        users = User.query.all()
        return jsonify({"message": "Query successful!", "users": [user.username for user in users]}), 200
    except Exception as e:
        return jsonify({"message": "Query failed!", "error": str(e)}), 500
