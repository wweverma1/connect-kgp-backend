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
            existing_rating = Rating.query.filter_by(rated_by_user_id=user_id).first()

            if existing_rating:
                existing_rating.created_at = datetime.now()
                existing_rating.rating = rating
                db.session.commit()
                return existing_rating
            else:
                new_rating = Rating(
                    created_at=datetime.now(),
                    rating=rating,
                    rated_by_user_id=user_id
                )
                db.session.add(new_rating)
                db.session.commit()
                return new_rating
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
