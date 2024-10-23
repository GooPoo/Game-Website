from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
#from flask_session import Session
from werkzeug.exceptions import Unauthorized
from datetime import datetime, date
from functools import wraps

from sqlalchemy.orm.exc import NoResultFound

from . import db, login
from app.forms import LoginForm, RegisterForm, TokenForm
from app.models import User, Game, Gamewordofday, Wordlewords, Guess, GameScore



@current_app.route('/')
def index():
    return render_template('base.html', title='Home')



@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username.', 'error')
            return redirect(url_for('login'))
        elif not user.check_password(form.password.data):
            flash('Invalid password.', 'error')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('login.html', title='Sign In', form=form)



@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now login.', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html', title='Register', form=form)



@current_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



####
# Main Daily Leaderboard Page
###
@current_app.route('/leaderboard', defaults={'leaderboard_date': None}, methods=['GET'])
@current_app.route('/leaderboard/<leaderboard_date>', methods=['GET'])
@login_required
def leaderboard(leaderboard_date=None):
     # If no date is provided, use today's date
    if leaderboard_date is None:
        leaderboard_date = date.today()
    else:
        # Convert the string parameter to a date object
        try:
            leaderboard_date = datetime.strptime(leaderboard_date, '%Y-%m-%d').date()
        except ValueError:
            # If the date format is invalid, default to today's date or handle the error as needed
            leaderboard_date = date.today()
    
    formatted_date = leaderboard_date.strftime('%d %B %Y')

    game_word_of_day = db.session.query(Gamewordofday.id).filter_by(date=leaderboard_date).first()

    if game_word_of_day:
        # Query the top 5 scores for today's word of the day
        leaderboard_data = (db.session.query(GameScore, User.username)
                            .join(Game, Game.id == GameScore.game_id)
                            .join(User, User.id == Game.user_id)
                            .filter(Game.game_word_id == game_word_of_day.id)
                            .order_by(GameScore.score.desc())
                            .limit(5)
                            .all())
    else:
        leaderboard_data = []

    return render_template('leaderboard.html', 
                           title='Leaderboard', 
                           leaderboard_data=leaderboard_data, 
                           current_user=current_user,
                           formatted_date=formatted_date)



####
# Main Wordle Game Page
###
@current_app.route('/wordleMain', methods=['GET'])
@login_required
def wordleMain():
    # Get the current date
    current_date = date.today()
    
    # Check if there is a Gamewordofday entry for the current date
    try:
        gamewordofday = Gamewordofday.query.filter_by(date=current_date).one()
    except NoResultFound:
        # If no Gamewordofday exists for the current date, create one with a random word
        random_word = Wordlewords.query.order_by(db.func.random()).first()
        gamewordofday = Gamewordofday(word=random_word.word, date=current_date)
        db.session.add(gamewordofday)
        db.session.commit()

    # Check if there is already a game for the current user and current Gamewordofday
    game = Game.query.filter_by(user_id=current_user.id, game_word_id=gamewordofday.id).first()

    # If no game exists, create a new game for the user
    if not game:
        game = Game(user_id=current_user.id, game_word_id=gamewordofday.id)
        db.session.add(game)
        db.session.commit()

    # Pass game_id to render_template
    game_id = game.id if game else None
    gamewordofday_word = gamewordofday.word if gamewordofday else None

    return render_template('wordleMain.html', title='Game', gamewordofday=gamewordofday_word, game_id=game_id)



####
# Display Finished Wordle Game Page
###
@current_app.route('/wordleDisplayFinishedGames/<int:game_id>', methods=['GET'])
@login_required
def wordleDisplayFinishedGames(game_id):

    if not game_id:
        return jsonify({'error': 'Game ID parameter missing'}), 400
    
    game = Game.query.filter_by(id=game_id).first()

    if not game:
        return jsonify({'error': 'Game not found or unauthorized'}), 404
    
    # Retrieve the user associated with this game
    user = game.user.username
    
    gameScore = GameScore.query.filter_by(game_id=game_id).first()

    if not gameScore:
        return jsonify({'error': 'Game Score not found or unauthorized'}), 404
    
    score = gameScore.score
    

    return render_template('wordleDisplayFinishedGames.html', 
                           title='Completed Game', 
                           user=user, 
                           game_id=game_id,
                           score=score)



###
# Returns Guesses of a Game
###
@current_app.route('/get_guesses/<int:game_id>', methods=['GET'])
@login_required
def get_guesses(game_id):

    # Ensure the game_id is provided and belongs to the current user
    if not game_id:
        return jsonify({'error': 'Game ID parameter missing'}), 400

    game = Game.query.filter_by(id=game_id).first()

    if not game:
        return jsonify({'error': 'Game not found or unauthorized'}), 404

    # Fetch guesses related to the game
    guesses = Guess.query.filter_by(game_id=game.id).order_by(Guess.guess_number).all()

    # Prepare guesses data in JSON serializable format
    guesses_data = [{
        'guess_number': guess.guess_number, 
        'guess_word': guess.guess_word, 
        'guess_score': guess.guess_score
        } for guess in guesses
    ]

    return jsonify(guesses_data)



###
# Returns Overlay data
###
@current_app.route('/get_overlay_data/<int:game_id>', methods=['GET'])
@login_required
def get_overlay_data(game_id):
    
    if not game_id:
        return jsonify({'error': 'Game ID parameter missing'}), 400

    # Fetch the game for the current user
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()
    
    if not game:
        return jsonify({'error': 'Game not found or unauthorized'}), 404

    # Fetch the number of attempts (number of guesses made)
    num_attempts = Guess.query.filter_by(game_id=game_id).count()

    # Fetch the score for the current game
    game_score = GameScore.query.filter_by(game_id=game_id).first()
    score = game_score.score if game_score else 0

    # Get the word of the day for the current date
    today = date.today()
    game_word_of_day = db.session.query(Gamewordofday.id).filter_by(date=today).first()

    if game_word_of_day:
        # Determine the user's position in the leaderboard for today's word
        leaderboard_data = (db.session.query(GameScore, User.username)
                            .join(Game, Game.id == GameScore.game_id)
                            .join(User, User.id == Game.user_id)
                            .filter(Game.game_word_id == game_word_of_day.id)
                            .order_by(GameScore.score.desc())
                            .all())

        # Find the user's position in the leaderboard
        position = next((i + 1 for i, (gs, username) in enumerate(leaderboard_data) if gs.game_id == game_id), None)
    else:
        position = None

    overlay_data = {
        'num_attempts': num_attempts, 
        'score': score,
        'position': position
    }
    
    return jsonify(overlay_data)



###
# User submission of a Word for a Game
###
@current_app.route('/submitWordleWord', methods=['POST'])
@login_required
def submitWordleWord():

    data = request.get_json()

    word = data.get('word')
    game_id = data.get('game_id')

    if not word or not game_id:
        return jsonify({'error': 'Missing word or game ID parameter'}), 400

    # Ensure the game_id belongs to the current user
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()
    if not game:
        return jsonify({'error': 'Game not found or unauthorized'}), 404
    
    # Check if the game is already complete
    if game.complete:
        return jsonify({'error': 'Game is already complete'}), 400

    # Validate the word
    feedback = validate_word(word, game_id)
    if feedback == "bad":
        return jsonify({'error': 'Invalid word'}), 400
    
    # Count the current number of guesses for this game
    guess_count = Guess.query.filter_by(game_id=game_id).count()
    
    # Save the valid guess to the database
    new_guess = Guess(
        game_id=game_id,
        guess_number=guess_count + 1,
        guess_word=word,
        guess_score=feedback
    )
    db.session.add(new_guess)

    # Check if the word is correct (i.e., all feedback is '2')
    if feedback == '22222' or guess_count + 1 >= 6:
        game.complete = True
        # Calculate and save the game score
        score = calculate_game_score(game_id)
        game_score = GameScore(game_id=game_id, score=score)
        db.session.add(game_score)

    db.session.commit()

    feedback_data = {'feedback': feedback}

    return jsonify(feedback_data)



def validate_word(word, game_id):

    # Check if the word exists in the Wordlewords table
    valid_word = Wordlewords.query.filter_by(word=word).first()
    if not valid_word:
        return "bad"
    
    # Get the target word for the game
    game = Game.query.filter_by(id=game_id).first()
    target_word = game.word_of_the_day.word

    feedback = [0] * 5  # Initialize feedback with all 0s
    target_word_letters = list(target_word)

    # Check for correct positions first
    for i in range(5):
        if word[i] == target_word[i]:
            feedback[i] = 2
            target_word_letters[i] = None  # Mark this letter as used

    # Check for correct letters in wrong positions
    for i in range(5):
        if feedback[i] != 2 and word[i] in target_word_letters:
            feedback[i] = 1
            target_word_letters[target_word_letters.index(word[i])] = None  # Mark this letter as used

    return ''.join(map(str, feedback))



def calculate_game_score(game_id):
    guesses = Guess.query.filter_by(game_id=game_id).all()

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



####
# Display Profile/Personal Stats Page
###
@current_app.route('/profile', defaults={'user_name': None}, methods=['GET'])
@current_app.route('/profile/<user_name>', methods=['GET'])
@login_required
def profile(user_name=None):

    if not user_name:
        user_name = current_user.username

    user = User.query.filter_by(username=user_name).first()

    if not user:
        return jsonify({'error': 'User is not found'}), 404

    recent_games = (
        db.session.query(Game, GameScore, Gamewordofday)
        .join(GameScore, Game.id == GameScore.game_id)
        .join(Gamewordofday, Game.game_word_id == Gamewordofday.id)
        .filter(Game.user_id == user.id)
        .order_by(Game.id.desc())
        .limit(5)
        .all()
    )

    top_scores = (
        db.session.query(GameScore, Gamewordofday)
        .join(Game, Game.id == GameScore.game_id)
        .join(Gamewordofday, Game.game_word_id == Gamewordofday.id)
        .filter(Game.user_id == user.id)
        .order_by(GameScore.score.desc())
        .limit(5)
        .all()
    )
    

    return render_template('profile.html', 
                           title=f'{user_name} Profile',
                           recent_games=recent_games,
                           top_scores=top_scores
                           )


###
# Landing Page for the API registration
###
@current_app.route('/apiPage', methods=['GET', 'POST'])
@login_required
def apiPage():
    form = TokenForm()

    if form.validate_on_submit():
        if form.generate_token.data:
            if current_user.api_token:
                flash('You already have an API token.', 'error')
            else:
                current_user.generate_api_token()
                flash('API token generated successfully.', 'success')
        elif form.revoke_token.data:
            if current_user.api_token:
                current_user.revoke_api_token()
                flash('API token revoked successfully.', 'success')
            else:
                flash('No API token found to revoke.', 'error')
        
        return redirect(url_for('apiPage'))

    return render_template('apiPage.html', form=form, api_token=current_user.api_token)



# FOR DEVELOPMENT ONLY, DELETE THIS ROUTE FOR PRODUCTION
@current_app.route('/delete_game', methods=['POST'])
@login_required
def delete_game():
    data = request.get_json()
    
    # Retrieve game_id from the JSON data and convert it to an integer
    game_id = data.get('game_id')
    
    if game_id is not None:
        try:
            game_id = int(game_id)
        except ValueError:
            return jsonify({'error': 'Invalid game ID format'}), 400
    
    
    # Ensure the game_id is provided and belongs to the current user
    if not game_id:
        return jsonify({'error': 'Game ID parameter missing'}), 400

    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()

    if not game:
        return jsonify({'error': 'Game not found or unauthorized'}), 404

    # Delete the game and its associated guesses
    db.session.delete(game)
    db.session.commit()

    return jsonify({'message': 'Game deleted successfully'})




# This error is sent when a user tries to bypass routes requiring @login_required while being 'un-logged in'.
@current_app.errorhandler(Unauthorized)
def unauthorized(error):
    flash("Login Required.", "error")
    return redirect(url_for('login'))