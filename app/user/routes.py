from flask import Blueprint

from app.user.controller import (
    signup,
    signin,
    verify,
    getFeeds,
    postFeed, 
    voteFeed,
    findUser,
    verifyUser,
    updatePassword,
    reportUser,
    addFriend,
    getFriends
)

user_api = Blueprint('user', __name__)

user_api.add_url_rule(rule='/signin', view_func=signin, methods=['POST'])
user_api.add_url_rule(rule='/signup', view_func=signup, methods=['POST'])
user_api.add_url_rule(rule='/signup-verify-email', view_func=verify, methods=['POST'])
user_api.add_url_rule(rule='/feeds', view_func=getFeeds, methods=['GET'])
user_api.add_url_rule(rule='/feed', view_func=postFeed, methods=['POST'])
user_api.add_url_rule(rule='/feed/vote', view_func=voteFeed, methods=['POST'])
user_api.add_url_rule(rule='/find-user', view_func=findUser, methods=['GET'])
user_api.add_url_rule(rule='/password-verify-email', view_func=verifyUser, methods=['POST'])
user_api.add_url_rule(rule='/update-password', view_func=updatePassword, methods=['POST'])
user_api.add_url_rule(rule='/report-user', view_func=reportUser, methods=['GET'])
user_api.add_url_rule(rule='/add-friend', view_func=addFriend, methods=['POST'])
user_api.add_url_rule(rule='/friends', view_func=getFriends, methods=['GET'])