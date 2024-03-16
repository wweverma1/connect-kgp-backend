# Standard library imports
import traceback

# Related third party imports
from sqlalchemy import ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime

# Local app specific imports
from app import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    friends = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    created_at = db.Column(db.DateTime, default=datetime.now())

    @staticmethod
    def create_user(name, email, password):
        try:
            user = User(
                name=name, 
                email=email, 
                password=password,
                rating=0,
                friends=[],
                created_at=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False