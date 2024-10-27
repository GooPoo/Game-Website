from app.models import GameAPI, GuessAPI, GameScoreAPI, Game, Guess, GameScore, Gamewordofday, Wordlewords, User

def validate_word(word, game_id):
    valid_word = Wordlewords.query.filter_by(word=word).first()
    if not valid_word:
        return "bad"
    
    game = Game.query.filter_by(id=game_id).first()
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




def validate_wordAPI(word, game_id):

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




def calculate_game_scoreAPI(game_id):
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