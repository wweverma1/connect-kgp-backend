# Standard library imports
import traceback
import uuid

# Related third party imports
from sqlalchemy import ARRAY
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime, timedelta

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
    last_active = db.Column(db.DateTime, default=datetime.now())
    last_promotional_mail = db.Column(db.DateTime, nullable=True, default=None)

    @staticmethod
    def create_user(name, email, password):
        try:
            user = User(
                name=name, 
                email=email, 
                password=password,
                rating=0,
                friends=[],
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
class Token(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    token = db.Column(db.String(36))
    created_at = db.Column(db.DateTime, default=datetime.now())
    valid_till = db.Column(db.DateTime, default=datetime.now()+timedelta(hours=24))

    @staticmethod
    def generate_and_add_token(user_id):
        try:
            access_token = str(uuid.uuid4())
            token = Token(user_id=user_id, token=access_token, created_at=datetime.now(), valid_till=datetime.now()+timedelta(hours=24))
            db.session.add(token)
            db.session.commit()
            return access_token
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    time = db.Column(db.DateTime, default=datetime.now())

    @staticmethod
    def add_log(user_id):
        try:
            log = Log(user_id=user_id, time=datetime.now())
            db.session.add(log)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False