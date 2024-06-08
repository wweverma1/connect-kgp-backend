from flask import (
    request, 
    jsonify,
)
from app.game.models import Legend
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from app import db
import random
import traceback

def getRandomHexCode():
    colors = [
        "#FF5733", "#33FF57", "#3366FF", "#FF33A1",
        "#66FF33", "#FF33CC", "#33A1FF", "#FF6633",
        "#33FFA1", "#CC33FF", "#33FF66", "#FFA133",
        "#33CCFF", "#FF3366", "#66FFA1", "#FFCC33"
    ]
    return random.choice(colors)

def getLegends():
    try:
        # Querying for distinct blocks
        created_for_values = db.session.query(Legend.created_for).distinct().all()
        print(created_for_values)
        # Fetching the legend for each available block
        response = {}
        for created_for in created_for_values:
            legend = Legend.query.filter_by(created_for=created_for[0]) \
                .order_by(func.array_length(Legend.liked_by, 1).desc(), Legend.created_at.asc()) \
                .first()

            if legend:
                response[created_for[0]] = {"name": legend.option_name, "color": legend.color}

        return jsonify({"legends": response}), 200

    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Couldn't fetch legends"}), 500

def postLegend():
    created_for = int(request.form['created_for'])
    created_by = int(request.form['user_id'])
    option_name = request.form['option_name'].strip()

    color = getRandomHexCode()

    legend = Legend.post_legend(created_for, option_name, color, created_by)

    if not legend:
        return jsonify({"error": "Some error occurred while posting your option"}), 500
    
    legends = Legend.query.filter_by(created_for=created_for).order_by(func.array_length(Legend.liked_by, 1).desc(), Legend.created_at.asc()).all()
    
    legend = legends[0]
    options = [{
        "option_id": legend.id,
        "option_name": legend.option_name,
        "liked_by": legend.liked_by
    } for legend in legends]

    return jsonify({"legend": {"name": legend.option_name, "color": legend.color}, "options": options}), 200

def voteLegend():
    created_for = request.form['created_for']
    option_id = request.form['option_id']
    user_id = int(request.form['user_id'])

    try:
        option = db.session.query(Legend).filter_by(id=option_id, created_for=created_for).one_or_none()
        
        if not option:
            return jsonify({"error": "Invalid option"}), 400
        
        if user_id in option.liked_by:
            option.liked_by.remove(user_id)
        else: 
            option.liked_by.append(user_id)
        db.session.commit()
        
        legends = Legend.query.filter_by(created_for=created_for).order_by(func.array_length(Legend.liked_by, 1).desc(), Legend.created_at.asc()).all()
    
        options = [{
            "option_id": legend.id,
            "option_name": legend.option_name,
            "liked_by": legend.liked_by
        } for legend in legends]

        return jsonify({"options": options}), 200
    except SQLAlchemyError as e:
        print(e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Couldn't register vote"}), 500
    
def getOptions():
    block_id = int(request.args.get('block'))

    if not block_id or block_id not in range(1, 9):
        return jsonify({"error": "invalid request"}), 400

    try:
        legends = Legend.query.filter_by(created_for=block_id).order_by(func.array_length(Legend.liked_by, 1).desc(), Legend.created_at.asc()).all()
    
        options = [{
            "option_id": legend.id,
            "option_name": legend.option_name,
            "liked_by": legend.liked_by
        } for legend in legends]

        return jsonify({"options": options}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500