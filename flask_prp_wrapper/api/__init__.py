"""API package."""

from flask import Blueprint

bp = Blueprint("api", __name__)

# Import routes to register them with the blueprint
from . import routes as routes  # noqa: E402, F401
