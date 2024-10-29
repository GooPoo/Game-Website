from flask import Blueprint

# Create a blueprint for the test routes
test_bp = Blueprint('test', __name__)

# Import the routes so they are registered
from .test_route import *
