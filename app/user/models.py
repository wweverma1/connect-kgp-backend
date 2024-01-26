# Standard library imports
from datetime import datetime
import traceback

# Related third party imports
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, name, email, password, dob=None):
        self.name = name
        self.email = email
        self.set_password(password)
        self.dob = dob

    @classmethod
    def create_user(cls, name, email, password, dob=None):
        try:
            user = cls(name=name, email=email, password=password, dob=dob)
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def is_email_registered(cls, email):
        return cls.query.filter_by(email=email).first() is not None

    def change_password(self, new_password):
        self.set_password(new_password)
        db.session.commit()