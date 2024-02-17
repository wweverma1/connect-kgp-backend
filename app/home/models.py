# Standard library imports
from datetime import datetime
import traceback

# Related third party imports
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import (
    db,
)
        
class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    rating = db.Column(db.Integer, default=0)
    rated_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    @staticmethod
    def post_rating(user_id, rating):
        try:
            rating = Rating(
                created_at=datetime.now(),
                rating=rating,
                rated_by_user_id=user_id
            )
            db.session.add(rating)
            db.session.commit()
            return rating
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
