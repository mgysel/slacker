'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  15/04/2020
Description:    Main file for backend, handles all connections & functions
'''
import os
import sys
import pickle
import threading
import json
from json import dumps
import urllib
from flask import Flask, request, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
from flask.json import jsonify
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from functools import wraps
from error import InputError, AccessError
from auth import auth_register, auth_login, auth_logout, \
auth_request, auth_reset
from user import user_profile, user_profile_setname, \
user_profile_setemail, user_profile_sethandle, \
user_profile_upload_photo
from channels import channels_list, channels_listall, channels_create
from channel import channel_invite, channel_details, \
channel_messages, channel_leave, channel_join, \
channel_addowner, channel_removeowner
from message import message_send, message_remove, \
message_edit, message_sendlater, message_react, \
message_unreact, message_pin, message_unpin
from other import standup_active, standup_start, usersAll, \
standup_send, admin_userpermission_change, admin_user_remove, search
import jwt
from dotenv import load_dotenv, find_dotenv, dotenv_values
load_dotenv(find_dotenv())

from objects.userObject import User

'''
########## Error Handler ##########
'''
def defaultHandler(error):
    '''
    Handles flask errors
    '''
    response = error.get_response()
    print('response', error, error.get_response())
    response.data = dumps({
        "code": error.code,
        "name": "System Error",
        "message": error.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)
APP.config['SECRET_KEY'] = 'your secret key'
APP.config['CORS_HEADERS'] = 'Content-Type'
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

APP.config['DATABASE_USERNAME'] = os.environ.get('DATABASE_USERNAME')
APP.config['DATABASE_PASSWORD'] = os.environ.get('DATABASE_PASSWORD')
APP.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
APP.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
APP.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
APP.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True

mail = Mail(APP)

'''
############### Main routes ###############
'''

'''
######### auth.py routes #########
'''
@APP.route('/auth/register', methods=['POST'])
@cross_origin()
def register_user():
    '''
    Registers a user
    '''
    usr_info = request.get_json()

    usr = auth_register(usr_info['email'], usr_info['password'], \
                        usr_info['name_first'], usr_info['name_last'])
    
    return dumps(usr)

@APP.route('/auth/login', methods=['POST'])
def login_user():
    '''
    Logs in a user and returns u_id and token
    '''
    usr_info = request.get_json()

    result = auth_login(usr_info['email'], usr_info['password'])

    return dumps(result)

@APP.route('/auth/logout', methods=['POST'])
def logout_user():
    '''
    Logs out a user and a is_success statement
    '''
    usr_info = request.get_json()

    result = auth_logout(usr_info['token'])

    return dumps(result)

@APP.route('/auth/passwordreset/request', methods=['POST'])
def request_reset():
    '''
    Takes in a users email and sets a request for a password reset, will email
    code for reset to email of user
    '''
    req_data = request.get_json()

    result = auth_request(APP.config['MAIL_USERNAME'], req_data['email'], mail)

    return dumps(result)

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def reset_reset():
    '''
    Takes in a reset_code and password then attempts to change password for the
    corresponding user
    '''
    req_data = request.get_json()

    result = auth_reset(req_data['reset_code'], req_data['new_password'])

    return dumps(result)

'''
######### user.py routes #########
'''
@APP.route('/user/profile', methods=['GET'])
def user_info():
    '''
    Collects and returns info on a given u_id
    '''
    token = request.args['token']
    u_id = int(request.args['u_id'])

    result = user_profile(token, u_id)

    return dumps(result)

@APP.route('/user/profile/setname', methods=['PUT'])
def user_change_name():
    '''
    Changes a users first and last name to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_setname(req_data['token'], \
                                req_data['name_first'], \
                                req_data['name_last'])

    return dumps(result)

@APP.route('/user/profile/setemail', methods=['PUT'])
def user_change_email():
    '''
    Changes a users email to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_setemail(req_data['token'], \
                                req_data['email'])

    return dumps(result)

@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_change_handle():
    '''
    Changes a users handle to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_sethandle(req_data['token'], \
                                req_data['handle_str'])

    return dumps(result)

@APP.route('/user/profiles/uploadphoto', methods=['PUT', 'GET', 'POST'])
def user_upload_photo():
    '''
    Uploads a users profile photo
    '''
    req_data = request.get_json()

    result = user_profile_upload_photo(req_data['token'], \
        req_data['img_url'], req_data['x_start'], req_data['y_start'], \
        req_data['x_end'], req_data['y_end'], BACKEND_URL)

    return dumps(result)

'''
######### channels.py routes #########
'''
@APP.route('/channels/list', methods=['GET'])
def users_channels():
    '''
    Collects and returns list of channels user is in
    '''
    token = request.args['token']

    result = channels_list(token)

    return dumps(result)

@APP.route('/channels/listall', methods=['GET'])
def all_channels():
    '''
    Collects and returns list of all channels
    '''
    token = request.args['token']

    result = channels_listall(token)

    return dumps(result)

@APP.route('/channels/create', methods=['POST'])
def create_channel():
    '''
    Creates a channel for the user according to specified preferences
    '''
    req_data = request.get_json()

    result = channels_create(req_data['token'], req_data['name'], \
    req_data['is_public'])

    return dumps(result)


'''
######### channel.py routes #########
'''
@APP.route('/channel/invite', methods=['POST'])
def invite_to_channel():
    '''
    Invites a user to channel, instantly adding them to it
    '''
    req_data = request.get_json()

    result = channel_invite(req_data['token'], int(req_data['channel_id']), \
    int(req_data['u_id']))

    return dumps(result)

@APP.route('/channel/details', methods=['GET'])
def details_channel():
    '''
    Returns details on channel such as name, members and owners
    '''
    token = request.args['token']
    channel_id = int(request.args['channel_id'])

    result = channel_details(token, channel_id)

    return dumps(result)

@APP.route('/channel/messages', methods=['GET'])
def messages_channel():
    '''
    Returns messages from the channel
    '''
    token = request.args['token']
    channel_id = int(request.args['channel_id'])
    start = int(request.args['start'])

    result = channel_messages(token, channel_id, start)

    return dumps(result)

@APP.route('/channel/leave', methods=['POST'])
def leave_channel():
    '''
    Lets a user leave a channel they are a member of
    '''
    req_data = request.get_json()

    channel_leave(req_data['token'], int(req_data['channel_id']))

    return dumps({})

@APP.route('/channel/join', methods=['POST'])
def join_channel():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_join(req_data['token'], int(req_data['channel_id']))

    return dumps({})

@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_addowner(req_data['token'], int(req_data['channel_id']), \
    int(req_data['u_id']))

    return dumps({})

@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_removeowner(req_data['token'], int(req_data['channel_id']), \
    int(req_data['u_id']))

    return dumps({})

'''
######### message.py routes #########
'''
@APP.route('/message/send', methods=['POST'])
def send_message():
    '''
    Sends a message to channel
    '''
    req_data = request.get_json()

    result = message_send(req_data['token'], int(req_data['channel_id']), \
    req_data['message'])

    return dumps(result)

@APP.route('/message/remove', methods=['DELETE'])
def remove_message():
    '''
    Sends a message at a specified time
    '''
    req_data = request.get_json()
    result = message_remove(req_data['token'], int(req_data['message_id']))
    return dumps(result)

@APP.route('/message/edit', methods=['PUT'])
def edit_message():
    '''
    Edits a message
    '''
    req_data = request.get_json()
    result = message_edit(req_data['token'], int(req_data['message_id']), \
    req_data['message'])
    return dumps(result)

@APP.route('/message/sendlater', methods=['POST'])
def sendlater_message():
    '''
    Send a message at a specified time
    '''
    req_data = request.get_json()

    message_sendlater(req_data['token'], int(req_data['channel_id']), req_data['message'], req_data['time_sent'])

    return dumps({})

@APP.route('/message/react', methods=['POST'])
def react_message():
    '''
    React to a message
    '''
    req_data = request.get_json()
    result = message_react(req_data['token'], int(req_data['message_id']), \
    int(req_data['react_id']))
    return dumps(result)

@APP.route('/message/unreact', methods=['POST'])
def unreact_message():
    '''
    Unreact to a message
    '''
    req_data = request.get_json()
    result = message_unreact(req_data['token'], int(req_data['message_id']), \
    int(req_data['react_id']))
    return dumps(result)

@APP.route('/message/pin', methods=['POST'])
def pin_message():
    '''
    Mark message as pinned
    '''
    req_data = request.get_json()
    result = message_pin(req_data['token'], int(req_data['message_id']))
    return dumps(result)

@APP.route('/message/unpin', methods=['POST'])
def unpin_message():
    '''
    Mark message as unpinned
    '''
    req_data = request.get_json()
    result = message_unpin(req_data['token'], int(req_data['message_id']))
    return dumps(result)

'''
######### other.py routes #########
'''

@APP.route('/standup/active', methods=['GET'])
def active_standup():
    '''
    Returns information on if standup is active
    '''
    token = request.args['token']
    channel_id = int(request.args['channel_id'])

    result = standup_active(token, channel_id)

    return dumps(result)

@APP.route('/standup/start', methods=['POST'])
def start_standup():
    '''
    Starts a standup for channel_id
    '''
    req_data = request.get_json()

    result = standup_start(req_data['token'], int(req_data['channel_id']), \
    req_data['length'])
    return dumps(result)

@APP.route('/standup/send', methods=['POST'])
def send_standup():
    '''
    Send a standup message
    '''
    req_data = request.get_json()

    standup_send(req_data['token'], int(req_data['channel_id']), \
    req_data['message'])

    return dumps({})

@APP.route('/users/all', methods=['GET'])
def user_list_all():
    '''
    Collects and returns info on all users
    '''
    token = request.args['token']

    result = usersAll(token)

    return dumps(result)

@APP.route('/search', methods=['GET'])
def route_search():
    '''
    Collects and returns info on all users
    '''
    token = request.args['token']
    query_str = request.args['query_str']

    result = search(token, query_str)

    return dumps(result)

@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_permission_change():
    '''
    Changes a users permission_id
    '''
    req_data = request.get_json()

    result = admin_userpermission_change(req_data['token'], \
    int(req_data['u_id']), int(req_data['permission_id']))

    return dumps(result)

@APP.route('/admin/user/remove', methods=['DELETE'])
def admin_delete_user():
    '''
    Deletes a user
    '''
    req_data = request.get_json()

    result = admin_user_remove(req_data['token'], \
                int(req_data['u_id']))

    return dumps(result)

@APP.route('/testing')
@cross_origin()
def index():
    # A welcome message to test our server
    return "<h1>Welcome to our medium-greeting-api!</h1>"

PORT = 2080
BACKEND_URL = "http://127.0.0.1:" + str(PORT)
if __name__ == "__main__":
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else PORT), debug=True)
    # APP.run(threaded=True, port=5000)
