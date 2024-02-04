# Standard library imports
import os

# Related third party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
from flask_cors import CORS

# Local app specific imports
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
SCHEMA_NAME = os.getenv("SCHEMA_NAME")

from app.home.routes import home_api
from app.user.routes import user_api

app.register_blueprint(home_api)
app.register_blueprint(user_api)

from app.utils.app_functions import (
    before_request,
    after_request,
)