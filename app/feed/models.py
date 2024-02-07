# Standard library imports
from datetime import datetime
from sqlalchemy import ARRAY
from sqlalchemy.ext.mutable import Mutable
import traceback

# Related third party imports
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import (
    db,
)

class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
        
class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)
    liked_by = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    disliked_by = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])

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
        
