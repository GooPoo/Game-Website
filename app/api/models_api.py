from flask import request, jsonify
from .auth import token_required
from datetime import date
from sqlalchemy.exc import NoResultFound

from app.models import GameAPI, GuessAPI, GameScoreAPI, Gamewordofday, Wordlewords
from app import db, csrf
from app.api import api_bp
from app.controllers import validate_wordAPI, calculate_game_scoreAPI


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
@api_bp.route('/wordle/submit/<int:gameid>/<string:word>', methods=['POST'])
@token_required
@csrf.exempt
def submit_word_api(user, gameid, word):

    if not word.isalpha() or len(word) != 5:
        return jsonify({'error': 'Word must be exactly 5 alphabetic characters'}), 400

    current_date = date.today()

    gamewordofday = Gamewordofday.query.filter_by(date=current_date).one_or_none()

    if not gamewordofday:
        return jsonify({'error': 'Word of the day not found'}), 400

    game = GameAPI.query.filter_by(id=gameid, game_word_id=gamewordofday.id).first()

    if not game:
        return jsonify({'error': 'Game is not playable'}), 400
    
    if game.complete:
        return jsonify({'error': 'Game is already complete'}), 400
    
    feedback = validate_wordAPI(word, gameid)

    if feedback == "bad":
        return jsonify({'error': 'Invalid word'}), 400
    
    guess_count = GuessAPI.query.filter_by(game_id=gameid).count()
    
    new_guess = GuessAPI(
        game_id=gameid,
        guess_number=guess_count + 1,
        guess_word=word,
        guess_score=feedback
    )
    db.session.add(new_guess)

    if feedback == '22222' or guess_count + 1 >= 6:
        game.complete = True
        score = calculate_game_scoreAPI(gameid)
        game_score = GameScoreAPI(game_id=gameid, score=score)
        db.session.add(game_score)

    db.session.commit()

    return jsonify({'feedback': feedback})



@api_bp.route('/wordle/status/<int:gameid>', methods=['GET'])
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
