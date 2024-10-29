from flask import Flask, current_app, request, jsonify, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
            get_remote_address,
            storage_uri="memory://",
            default_limits=["400 per day", "100 per hour"]
        )

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        # Import routes and models here to avoid circular imports
        from app import routes, models

        # Register blueprints
        from app.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

        # Define the user loader function for Flask-Login
        @login.user_loader
        def load_user(user_id):
            from app.models import User
            return User.query.get(int(user_id))
        
        # Optional: skips limits in specific cases
        @limiter.request_filter
        def exempt_from_limit():
            return False

        @app.errorhandler(429)
        def ratelimit_exceeded(e):
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'You have exceeded the allowed number of requests If this is a mistake or you want to increase your limit, get in contact with me :).'
                }), 429
            else:
                return render_template('rate_limit_exceeded.html',  title='Rate Limit Exceeded'), 429

        return app