# Standard library imports
from datetime import datetime
from datetime import timedelta
import traceback
import random

# Related third party imports
from sqlalchemy.exc import SQLAlchemyError

# Local app specific imports
from app import (
    db,
)

class OTP(db.Model):
    __tablename__ = 'otp'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    created_for = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(5), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(minutes=10))

    @staticmethod
    def generate_otp(email):
        try:
            otp = OTP(
                created_at=datetime.now(),
                created_for=email,
                code=str(random.randint(10000, 99999)),
                expiry=datetime.now() + timedelta(minutes=10),
            )
            db.session.add(otp)
            db.session.commit()
            return otp
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            db.session.rollback()
            return False