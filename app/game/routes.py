from flask import Blueprint

from app.game.controller import (
    getLegends,
    getOptions,
    postLegend,
    voteLegend
)

game_api = Blueprint('game', __name__)

game_api.add_url_rule(rule='/legends', view_func=getLegends, methods=['GET'])
game_api.add_url_rule(rule='/legend/options', view_func=getOptions, methods=['GET'])
game_api.add_url_rule(rule='/legend', view_func=postLegend, methods=['POST'])
game_api.add_url_rule(rule='/legend/vote', view_func=voteLegend, methods=['POST'])

