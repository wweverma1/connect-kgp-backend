# Standard library imports
import os

# Related third party imports
from flask import Flask
from dotenv import load_dotenv

# Local app specific imports
load_dotenv()

app = Flask(__name__)

from app.home.routes import home_api
from app.user.routes import user_api

app.register_blueprint(home_api)
app.register_blueprint(user_api)

from app.utils.app_functions import (
    before_request,
    after_request,
)