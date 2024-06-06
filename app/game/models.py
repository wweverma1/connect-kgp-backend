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
        
class Legend(db.Model):
    __tablename__ = 'legend'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    created_for = db.Column(db.Integer, nullable=False)
    option_name = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    liked_by = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    
    @staticmethod
    def post_legend(created_for, option_name, color, created_by):
        try:
            legend = Legend(
                created_at=datetime.now(),
                created_for=created_for,
                option_name=option_name,
                color=color,
                liked_by=[created_by]
            )
            db.session.add(legend)
            db.session.commit()
            return legend
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False