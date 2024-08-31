from flask import Flask, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    with app.app_context():
        # Import routes and models here to avoid circular imports
        from app import routes, models

        # Define the user loader function for Flask-Login
        @login.user_loader
        def load_user(user_id):
            from app.models import User
            return User.query.get(int(user_id))

        return app