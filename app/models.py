from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from secrets import token_urlsafe
from app import db

Column, Integer, String, Boolean, Date, ForeignKey, Model, relationship = (
    db.Column, db.Integer, db.String, db.Boolean, db.Date, db.ForeignKey, db.Model, db.relationship
)

class User(UserMixin, Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    api_token = db.Column(db.String(64), unique=True, nullable=True, default=None)
    
    db.Index('idx_api_token', api_token)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_api_token(self):
        self.api_token = token_urlsafe(32)
        db.session.commit()

    def revoke_api_token(self):
        self.api_token = None
        db.session.commit()

    games = relationship('Game', order_by='Game.id', back_populates='user')


class Wordlewords(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)


class Gamewordofday(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)
    date = Column(Date, nullable=False, unique=True)
    
    games = relationship('Game', back_populates='word_of_the_day')


class Game(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    game_word_id = Column(Integer, ForeignKey('gamewordofday.id'), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)
    
    user = relationship('User', back_populates='games')
    word_of_the_day = relationship('Gamewordofday', back_populates='games')
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
    
    game = relationship('Game', back_populates='guesses')

# Indexes for Guess table for fast lookup
db.Index('idx_game_id', Guess.game_id)
db.Index('idx_game_id_guess_number', Guess.game_id, Guess.guess_number)
