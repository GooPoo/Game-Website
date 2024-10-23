from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import auth, models_api, token_api
