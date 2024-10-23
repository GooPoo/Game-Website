from flask import request, jsonify
from .auth import token_required
from app.models import Game, Guess
from app import db
from app.api import api_bp

@api_bp.route('/submitWord', methods=['POST'])
@token_required
def submit_word_api(user):
    data = request.get_json()
    word = data.get('word')
    game_id = data.get('game_id')

    if not word or not game_id:
        return jsonify({'error': 'Missing word or game ID'}), 400
    
    # Use game_id and user information to validate and process the guess
    # Assuming you have a function to handle this
    feedback = validate_word(word, game_id)
    
    if feedback == "bad":
        return jsonify({'error': 'Invalid word'}), 400

    # Return the feedback as a response
    return jsonify({'feedback': feedback})

# You can add other API-related routes here, such as:
# - Starting a new game
# - Getting the status of a current game
# - Fetching word of the day, etc.
