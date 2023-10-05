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
from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from error import InputError, AccessError
from auth import auth_register, auth_logout, auth_login, \
auth_request, auth_reset
from user import user_profile, user_profile_setname, \
user_profile_setemail, user_profile_sethandle, \
user_profile_upload_photo, userfromtoken
from channels import channels_list, channels_listall, channels_create
from channel import channel_invite, channel_details, \
channel_messages, channel_leave, channel_join, \
channel_addowner, channel_removeowner
from message import message_send, message_remove, \
message_edit, message_sendlater, message_react, \
message_unreact, message_pin, message_unpin, hangman
from other import standup_active, standup_start, usersAll, \
standup_send, admin_userpermission_change, admin_user_remove

sys.path.append("./src")

'''
########## Data Variables and Setup ##########
'''
USER_DATA = {'num_users': 0, 'users': []}
CHANNEL_DATA = {'num_channels': 0, 'channels': []}
MESSAGE_DATA = {'channels': []}
HANGMAN_DATA = {'channels': []}

# # Loads USER_DATA if available
# if os.path.exists('src/user_data.p'):
#     USER_DATA = pickle.load(open('src/user_data.p', 'rb'))

# # Loads CHANNEL_DATA if available
# if os.path.exists('src/channel_data.p'):
#     CHANNEL_DATA = pickle.load(open('src/channel_data.p', 'rb'))

# # Loads MESSAGE_DATA if available
# if os.path.exists('src/message_data.p'):
#     MESSAGE_DATA = pickle.load(open('src/message_data.p', 'rb'))

# # Loads HANGMAN_DATA if available
# if os.path.exists('src/hangman_data.p'):
#     HANGMAN_DATA = pickle.load(open('src/hangman_data.p', 'rb'))

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

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

'''
############### Main routes ###############
'''

'''
######### auth.py routes #########
'''
@APP.route('/auth/register', methods=['POST'])
def register_user():
    '''
    Registers a user and returns u_id and token
    '''
    usr_info = request.get_json()

    usr = auth_register(usr_info['email'], usr_info['password'], \
                        usr_info['name_first'], usr_info['name_last'], \
                        USER_DATA)

    return dumps(usr)


@APP.route('/auth/logout', methods=['POST'])
def logout_user():
    '''
    Logs out a user and a is_success statement
    '''
    usr_info = request.get_json()

    result = auth_logout(usr_info['token'], USER_DATA)

    return dumps(result)


@APP.route('/auth/login', methods=['POST'])
def login_user():
    '''
    Logs in a user and returns u_id and token
    '''
    usr_info = request.get_json()

    result = auth_login(usr_info['email'], usr_info['password'], USER_DATA)

    return dumps(result)


@APP.route('/auth/passwordreset/request', methods=['POST'])
def request_reset():
    '''
    Takes in a users email and sets a request for a password reset, will email
    code for reset to email of user
    '''
    req_data = request.get_json()

    result = auth_request(req_data['email'], USER_DATA)

    return dumps(result)


@APP.route('/auth/passwordreset/reset', methods=['POST'])
def reset_reset():
    '''
    Takes in a reset_code and password then attempts to change password for the
    corresponding user
    '''
    req_data = request.get_json()

    result = auth_reset(req_data['reset_code'], req_data['new_password'], USER_DATA)

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

    result = user_profile(token, u_id, USER_DATA)

    return dumps(result)


@APP.route('/user/profile/setname', methods=['PUT'])
def user_change_name():
    '''
    Changes a users first and last name to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_setname(req_data['token'], \
                                req_data['name_first'], \
                                req_data['name_last'], USER_DATA)

    return dumps(result)


@APP.route('/user/profile/setemail', methods=['PUT'])
def user_change_email():
    '''
    Changes a users email to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_setemail(req_data['token'], \
                                req_data['email'], USER_DATA)

    return dumps(result)


@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_change_handle():
    '''
    Changes a users handle to what is requested
    '''
    req_data = request.get_json()

    result = user_profile_sethandle(req_data['token'], \
                                req_data['handle_str'], USER_DATA)

    return dumps(result)


@APP.route('/user/profile/uploadphoto', methods=['PUT', 'GET'])
def user_upload_photo():
    '''
    Uploads a users profile photo
    '''
    req_data = request.get_json()

    result = user_profile_upload_photo(req_data['token'], \
        req_data['img_url'], req_data['x_start'], req_data['y_start'], \
        req_data['x_end'], req_data['y_end'], USER_DATA)

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

    result = channels_list(token, CHANNEL_DATA, USER_DATA)

    return dumps(result)


@APP.route('/channels/listall', methods=['GET'])
def all_channels():
    '''
    Collects and returns list of all channels
    '''
    token = request.args['token']

    result = channels_listall(token, CHANNEL_DATA, USER_DATA)

    return dumps(result)


@APP.route('/channels/create', methods=['POST'])
def create_channel():
    '''
    Creates a channel for the user according to specified preferences
    '''
    req_data = request.get_json()

    result = channels_create(req_data['token'], req_data['name'], \
    req_data['is_public'], CHANNEL_DATA, USER_DATA)

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
    int(req_data['u_id']), CHANNEL_DATA, USER_DATA)

    return dumps(result)


@APP.route('/channel/details', methods=['GET'])
def details_channel():
    '''
    Returns details on channel such as name, members and owners
    '''
    token = request.args['token']
    channel_id = int(request.args['channel_id'])

    result = channel_details(token, channel_id, \
    CHANNEL_DATA, USER_DATA)

    return dumps(result)


@APP.route('/channel/messages', methods=['GET'])
def messages_channel():
    '''
    Returns messages from the channel
    '''
    token = request.args['token']
    channel_id = int(request.args['channel_id'])
    start = int(request.args['start'])

    result = channel_messages(token, channel_id, \
    start, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)

    return dumps(result)


@APP.route('/channel/leave', methods=['POST'])
def leave_channel():
    '''
    Lets a user leave a channel they are a member of
    '''
    req_data = request.get_json()

    channel_leave(req_data['token'], int(req_data['channel_id']), \
    CHANNEL_DATA, USER_DATA)

    return dumps({})


@APP.route('/channel/join', methods=['POST'])
def join_channel():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_join(req_data['token'], int(req_data['channel_id']), \
    CHANNEL_DATA, USER_DATA)

    return dumps({})


@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_addowner(req_data['token'], int(req_data['channel_id']), \
    int(req_data['u_id']), CHANNEL_DATA, USER_DATA)

    return dumps({})


@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    '''
    Lets a user join a channel
    '''
    req_data = request.get_json()

    channel_removeowner(req_data['token'], int(req_data['channel_id']), \
    int(req_data['u_id']), CHANNEL_DATA, USER_DATA)

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
    req_data['message'], USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)

    return dumps(result)

@APP.route('/message/remove', methods=['DELETE'])
def remove_message():
    '''
    Sends a message at a specified time
    '''
    req_data = request.get_json()
    result = message_remove(req_data['token'], int(req_data['message_id']), \
    USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)

@APP.route('/message/edit', methods=['PUT'])
def edit_message():
    '''
    Edits a message
    '''
    req_data = request.get_json()
    result = message_edit(req_data['token'], int(req_data['message_id']), \
    req_data['message'], USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)

@APP.route('/message/sendlater', methods=['POST'])
def sendlater_message():
    '''
    Send a message at a specified time
    '''
    req_data = request.get_json()

    message_sendlater(int(req_data['u_id']), int(req_data['channel_id']), \
    req_data['message'], req_data['time_sent'], USER_DATA, \
    CHANNEL_DATA, MESSAGE_DATA)

    return dumps({})

@APP.route('/message/react', methods=['POST'])
def react_message():
    '''
    React to a message
    '''
    req_data = request.get_json()
    result = message_react(req_data['token'], int(req_data['message_id']), \
    int(req_data['react_id']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)

@APP.route('/message/unreact', methods=['POST'])
def unreact_message():
    '''
    Unreact to a message
    '''
    req_data = request.get_json()
    result = message_unreact(req_data['token'], int(req_data['message_id']), \
    int(req_data['react_id']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)

@APP.route('/message/pin', methods=['POST'])
def pin_message():
    '''
    Mark message as pinned
    '''
    req_data = request.get_json()
    result = message_pin(req_data['token'], int(req_data['message_id']), \
    USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)

@APP.route('/message/unpin', methods=['POST'])
def unpin_message():
    '''
    Mark message as unpinned
    '''
    req_data = request.get_json()
    result = message_unpin(req_data['token'], int(req_data['message_id']), \
    USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
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

    result = standup_active(token, channel_id, \
    USER_DATA, CHANNEL_DATA)

    return dumps(result)


@APP.route('/standup/start', methods=['POST'])
def start_standup():
    '''
    Starts a standup for channel_id
    '''
    req_data = request.get_json()

    result = standup_start(req_data['token'], int(req_data['channel_id']), \
    req_data['length'], USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    return dumps(result)


@APP.route('/standup/send', methods=['POST'])
def send_standup():
    '''
    Send a standup message
    '''
    req_data = request.get_json()

    standup_send(req_data['token'], int(req_data['channel_id']), \
    req_data['message'], USER_DATA, CHANNEL_DATA,)

    return dumps({})


@APP.route('/users/all', methods=['GET'])
def user_list_all():
    '''
    Collects and returns info on all users
    '''
    token = request.args['token']

    result = usersAll(token, USER_DATA)

    return dumps(result)


@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_permission_change():
    '''
    Changes a users permission_id
    '''
    req_data = request.get_json()

    result = admin_userpermission_change(req_data['token'], \
    int(req_data['u_id']), int(req_data['permission_id']), USER_DATA)

    return dumps(result)


@APP.route('/admin/user/remove', methods=['DELETE'])
def admin_delete_user():
    '''
    Deletes a user
    '''
    req_data = request.get_json()

    result = admin_user_remove(req_data['token'], \
                int(req_data['u_id']), USER_DATA)

    return dumps(result)


'''
######### Data related routes #########
'''
@APP.route('/workspace/reset', methods=['POST'])
def reset_data():
    '''
    Resets server data
    '''
    global USER_DATA, CHANNEL_DATA, MESSAGE_DATA
    USER_DATA = {'num_users': 0, 'users': []}
    CHANNEL_DATA = {'num_channels': 0, 'channels': []}
    MESSAGE_DATA = {'channels': []}
    HANGMAN_DATA = {'channels': []}

    return dumps({})


def save_data():
    '''
    Saves server data via pickle
    '''
    global USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA

    # Saves USER_DATA
    with open('src/user_data.p', 'wb') as FILE:
        pickle.dump(USER_DATA, FILE)

    # Saves CHANNEL_DATA
    with open('src/channel_data.p', 'wb') as FILE:
        pickle.dump(CHANNEL_DATA, FILE)

    # Saves MESSAGE_DATA
    with open('src/message_data.p', 'wb') as FILE:
        pickle.dump(MESSAGE_DATA, FILE)

    # Saves HANGMAN_DATA
    with open('src/hangman_data.p', 'wb') as FILE:
        pickle.dump(HANGMAN_DATA, FILE)


def save_timer():
    '''
    Timer to auto-saves server data every second
    '''
    timer = threading.Timer(1.0, save_timer)
    timer.start()
    save_data()
# Starts auto-save timer
save_timer()


if __name__ == "__main__":
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 2080))
