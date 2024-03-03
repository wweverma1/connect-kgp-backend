# Standard library imports
from datetime import datetime
from sqlalchemy import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList
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
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(1), nullable=False)
    liked_by = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    disliked_by = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    parent_feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    
    parent_feed = relationship('Feed', remote_side=[id])

    @staticmethod
    def post_feed(user_id, content, icon, parent_feed_id=None):
        try:
            feed = Feed(
                created_at=datetime.now(),
                created_by=user_id,
                content=content,
                icon=icon,
                liked_by=[],
                disliked_by=[],
                parent_feed_id=parent_feed_id
            )
            db.session.add(feed)
            db.session.commit()
            return feed
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False
        
