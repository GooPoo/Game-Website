from flask import request, jsonify
from .auth import token_required
from datetime import date
from sqlalchemy.exc import NoResultFound

from app.models import GameAPI, GuessAPI, GameScoreAPI, Gamewordofday, Wordlewords
from app import db, csrf
from app.api import api_bp

def validate_word(word, game_id):

    valid_word = Wordlewords.query.filter_by(word=word).first()
    if not valid_word:
        return "bad"
    
    game = GameAPI.query.filter_by(id=game_id).first()
    target_word = game.word_of_the_day.word

    feedback = [0] * 5 
    target_word_letters = list(target_word)

    for i in range(5):
        if word[i] == target_word[i]:
            feedback[i] = 2
            target_word_letters[i] = None 

    for i in range(5):
        if feedback[i] != 2 and word[i] in target_word_letters:
            feedback[i] = 1
            target_word_letters[target_word_letters.index(word[i])] = None 

    return ''.join(map(str, feedback))



def calculate_game_score(game_id):
    guesses = GuessAPI.query.filter_by(game_id=game_id).all()

    total_feedback_score = 0
    won_game = False

    for guess in guesses:
        score_str = guess.guess_score
        total_feedback_score += sum(int(char) for char in score_str)
        if score_str == '22222':
            won_game = True

    guess_count = len(guesses)

    if won_game:
        final_score = total_feedback_score * (2 ** (7 - guess_count))
    else:
        final_score = total_feedback_score
    return final_score


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
    current_date = date.today()

    if not word:
        return jsonify({'error': 'Missing word'}), 400

    gamewordofday = Gamewordofday.query.filter_by(date=current_date).one_or_none()

    if not gamewordofday:
        return jsonify({'error': 'Fetching word of the day'}), 400

    game = GameAPI.query.filter_by(id=gameid, game_word_id=gamewordofday.id).first()

    if not game:
        return jsonify({'error': 'Game is not playable'}), 400
    
    feedback = validate_word(word, gameid)

    if feedback == "bad":
        return jsonify({'error': 'Invalid word'}), 400
    
    new_guess = GuessAPI(
        game_id=gameid,
        guess_number=len(game.guesses) + 1,
        guess_word=word,
        guess_score=feedback
    )
    db.session.add(new_guess)

    guess_count = len(game.guesses)
    if feedback == '22222' or guess_count + 1 >= 6:
        game.complete = True

        score = calculate_game_score(gameid)
        game_score = GameScoreAPI(game_id=gameid, score=score)
        db.session.add(game_score)

    db.session.commit()

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
