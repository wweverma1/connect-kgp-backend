from flask import (
    request, 
    jsonify
)

from app import db
from app.home.models import Rating
def home():
    return "ConnectKGP", 200

def postRating():
    rating = request.form['rating']
    user_id = request.form['user_id']

    rating = Rating.post_rating(user_id, rating)
    if not rating:
        return jsonify({"error": "Some error occured while posting your rating"}), 500    
    return jsonify({"message": "rating submitted", "rating": rating.rating}), 200

def getRating():
    response = {}
    user_id = request.args.get('user_id')

    if user_id:
        user_rating = db.session.query(Rating.rating).filter_by(rated_by_user_id=user_id).first()
        if user_rating:
            response['user_rating'] = user_rating[0]

    ratings = db.session.query(Rating.rating).all()

    total_ratings = len(ratings)
    if total_ratings > 0:
        avg_rating = sum(rating[0] for rating in ratings) / total_ratings
    else:
        avg_rating = 0

    response["avg_rating"] = avg_rating
    return jsonify(response), 200