from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

Column, Integer, String, Boolean, Date, ForeignKey, Model, relationship = (
    db.Column, db.Integer, db.String, db.Boolean, db.Date, db.ForeignKey, db.Model, db.relationship
)



class User(UserMixin, Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    # Generates a salted password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Checks the password against the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # The Games played by a User
    games = relationship('Game', order_by='Game.id', back_populates='user')



class Wordlewords(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)



class Gamewordofday(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)
    date = Column(Date, nullable=False, unique=True)



class Game(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    game_word_id = Column(Integer, ForeignKey('gamewordofday.id'), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)
    
    # The User who played a Game
    user = relationship('User', back_populates='games')
    # The Word of the Game
    word_of_the_day = relationship('Gamewordofday')
    # The Guesses made in the Game
    guesses = relationship('Guess', back_populates='game', cascade='all, delete-orphan')
    game_score = relationship('GameScore', uselist=False, back_populates='game', cascade='all, delete-orphan')



class GameScore(Model):
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)
    score = Column(Integer, nullable=False)
    
    game = relationship('Game', back_populates='game_score')



class Guess(Model):
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)
    guess_number = Column(Integer, nullable=False)
    guess_word = Column(String(5), nullable=False)
    guess_score = Column(String(5), nullable=False)
    
    # The Game where Guess originated
    game = relationship('Game', back_populates='guesses')



# Create indexes
db.Index('idx_game_id', Guess.game_id)
db.Index('idx_game_id_guess_number', Guess.game_id, Guess.guess_number)
