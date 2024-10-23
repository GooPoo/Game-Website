from flask import jsonify, request, flash
from flask_login import current_user
from app import db
from app.api import api_bp

@api_bp.route('/generate_token', methods=['POST'])
def generate_token():
    if current_user.is_authenticated:
        if not current_user.api_token:
            current_user.generate_api_token()
            flash('API token generated successfully.', 'success')
        else:
            flash('You already have an API token.', 'error')
    else:
        flash('You must be logged in to generate a token.', 'error')

    return jsonify({'api_token': current_user.api_token})

@api_bp.route('/revoke_token', methods=['POST'])
def revoke_token():
    if current_user.is_authenticated:
        if current_user.api_token:
            current_user.revoke_api_token()
            flash('API token revoked successfully.', 'success')
        else:
            flash('No API token found to revoke.', 'error')
    else:
        flash('You must be logged in to revoke a token.', 'error')

    return jsonify({'message': 'Token revoked'})
