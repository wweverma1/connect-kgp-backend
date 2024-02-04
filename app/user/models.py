# Standard library imports
import traceback

# Related third party imports
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    rating = db.Column(db.Integer, default=0)

    @staticmethod
    def create_user(name, email, dob, password):
        try:
            user = User(
                name=name, 
                email=email, 
                dob=dob, 
                password=password,
                rating=0
            )
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False