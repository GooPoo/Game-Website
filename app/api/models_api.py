from flask import request, jsonify
from .auth import token_required
from app.models import GameAPI, GuessAPI, GameScoreAPI, Gamewordofday, Wordlewords
from app import db, csrf
from app.api import api_bp
from datetime import date
from sqlalchemy.exc import NoResultFound

# List all games that the user has participated in, with scores and status
@api_bp.route('/wordle', methods=['GET'])
@token_required
def list_games_api(user):
    games = GameAPI.query.filter_by(user_id=user.id).all()

    if not games:
        return jsonify({'message': 'No games found'}), 404

    games_list = []
    for game in games:
        game_data = {
            'game_id': game.id,
            'completed': game.complete,
            'score': game.game_score.score if game.game_score else None
        }
        games_list.append(game_data)

    return jsonify({'games': games_list}), 200

    

# Create a new game for the user if none exists
@api_bp.route('/wordle/create', methods=['POST'])
@token_required
@csrf.exempt
def create_game_api(user):
    current_date = date.today()
    
    try:
        gamewordofday = Gamewordofday.query.filter_by(date=current_date).one()
    except NoResultFound:
        random_word = Wordlewords.query.order_by(db.func.random()).first()
        if not random_word:
            return jsonify({'error': 'No valid word available'}), 500
            
        gamewordofday = Gamewordofday(word=random_word.word, date=current_date)
        db.session.add(gamewordofday)
        db.session.commit()
    
    existing_game = GameAPI.query.filter_by(user_id=user.id, game_word_id=gamewordofday.id).first()
    if existing_game:
        return jsonify({'message': 'Game already exists', 'game_id': existing_game.id}), 200

    new_game = GameAPI(user_id=user.id, game_word_id=gamewordofday.id)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({'message': 'New game created', 'game_id': new_game.id}), 201



# Submit a word for the game
@api_bp.route('/wordle/<int:gameid>/submit', methods=['POST'])
@token_required
@csrf.exempt
def submit_word_api(user, gameid):
    data = request.get_json()
    word = data.get('word')

    if not word:
        return jsonify({'error': 'Missing word'}), 400
    
    feedback = validate_word(word, gameid)

    if feedback == "bad":
        return jsonify({'error': 'Invalid word'}), 400

    return jsonify({'feedback': feedback})



@api_bp.route('/wordle/<int:gameid>/status', methods=['GET'])
@token_required
def game_status_api(user, gameid):
    game = GameAPI.query.filter_by(id=gameid, user_id=user.id).first()

    if not game:
        return jsonify({'error': 'Game not found'}), 404

    guesses = GuessAPI.query.filter_by(game_id=game.id).all()

    guesses_list = [{
        'guess_number': guess.guess_number,
        'guess_word': guess.guess_word,
        'guess_score': guess.guess_score
    } for guess in guesses]

    response_data = {
        'game_id': game.id,
        'status': 'completed' if game.complete else 'ongoing',
        'guesses': guesses_list
    }

    return jsonify(response_data), 200




# You can add other API-related routes here, such as:
# - Starting a new game
# - Getting the status of a current game
# - Fetching word of the day, etc.
