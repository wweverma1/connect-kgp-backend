# Standard library imports
from datetime import datetime
from sqlalchemy import ARRAY
import traceback

# Related third party imports
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import (
    db,
)

class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)
    liked_by = db.Column(ARRAY(db.Integer), default=[])
    disliked_by = db.Column(ARRAY(db.Integer), default=[])


    @staticmethod
    def post_feed(content):
        try:
            feed = Feed(
                created_at=datetime.now(),
                content=content,
                rating=0,
                liked_by=[],
                disliked_by=[]
            )
            db.session.add(feed)
            db.session.commit()
            return feed
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False