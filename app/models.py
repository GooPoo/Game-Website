from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from secrets import token_urlsafe
from app import db
from sqlalchemy.ext.declarative import declared_attr

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
    api_games = relationship('GameAPI', order_by='GameAPI.id', back_populates='user')





class Wordlewords(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)


class Gamewordofday(Model):
    id = Column(Integer, primary_key=True)
    word = Column(String(5), nullable=False)
    date = Column(Date, nullable=False, unique=True)
    
    games = relationship('Game', back_populates='word_of_the_day')
    api_games = relationship('GameAPI', back_populates='word_of_the_day')





class BaseGame(Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    game_word_id = Column(Integer, ForeignKey('gamewordofday.id'), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)


class Game(BaseGame):
    __tablename__ = 'game'
    
    user = relationship('User', back_populates='games')
    word_of_the_day = relationship('Gamewordofday', back_populates='games')
    guesses = relationship('Guess', back_populates='game', cascade='all, delete-orphan')
    game_score = relationship('GameScore', uselist=False, back_populates='game', cascade='all, delete-orphan')


class GameAPI(BaseGame):
    __tablename__ = 'game_api'
    
    user = relationship('User', back_populates='api_games')
    word_of_the_day = relationship('Gamewordofday', back_populates='api_games')
    guesses = relationship('GuessAPI', back_populates='game', cascade='all, delete-orphan')
    game_score = relationship('GameScoreAPI', uselist=False, back_populates='game', cascade='all, delete-orphan')





class BaseGameScore(Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)


class GameScore(BaseGameScore):
    __tablename__ = 'game_score'

    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)

    game = relationship('Game', back_populates='game_score')


class GameScoreAPI(BaseGameScore):
    __tablename__ = 'game_score_api'

    game_id = Column(Integer, ForeignKey('game_api.id'), nullable=False)

    game = relationship('GameAPI', back_populates='game_score')





class BaseGuess(Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, nullable=False)
    guess_number = Column(Integer, nullable=False)
    guess_word = Column(String(5), nullable=False)
    guess_score = Column(String(5), nullable=False)


class Guess(BaseGuess):
    __tablename__ = 'guess'

    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)

    game = relationship('Game', back_populates='guesses')


class GuessAPI(BaseGuess):
    __tablename__ = 'guess_api'

    game_id = Column(Integer, ForeignKey('game_api.id'), nullable=False)

    game = relationship('GameAPI', back_populates='guesses')





db.Index('idx_game_id', Guess.game_id)
db.Index('idx_game_id_guess_number', Guess.game_id, Guess.guess_number)

db.Index('idx_apigame_id', GuessAPI.game_id)
db.Index('idx_apigame_id_guess_number', GuessAPI.game_id, GuessAPI.guess_number)
