'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  16/04/2020
Description:    search, standup_start, standup_active, standup_send,
                admin_user_permission_change functions for slackr
'''

from datetime import datetime, timedelta
from threading import Timer
from error import AccessError, InputError
from helpers import queryUserData, isValidUser
from channel import get_channel_data
from message import message_send

'''
########## Helper functions ##########
'''

def is_valid_channel(channel_id, CHANNEL_DATA):
    '''
    Checks if the channel_id is valid.
    Return True if valid, false otherwise
    '''
    return len(get_channel_data(channel_id, CHANNEL_DATA))

def is_user_in_channel(token, channel_id, CHANNEL_DATA, USER_DATA):
    '''
    Checks if user is a member of channel_id
    Returns True if user in channel
    Returns False otherwise
    '''
    u_id = queryUserData('token', token, USER_DATA)['u_id']
    members = get_channel_data(channel_id, CHANNEL_DATA)['members']
    return len([member for member in members if member['u_id'] == u_id])

def is_standup_in_session(channel_id, CHANNEL_DATA):
    '''
    Determines if standup for channel_id is in session
    Returns True if in session, False otherwise
    '''
    this_channel = get_channel_data(channel_id, CHANNEL_DATA)
    return this_channel['standup']['is_active']

def get_standup_data(channel_id, CHANNEL_DATA):
    '''
    Returns dictionary of standup data corresponding to channel_id
    '''
    return get_channel_data(channel_id, CHANNEL_DATA)['standup']

def update_standup_key(channel_id, key, value, CHANNEL_DATA):
    '''
    Updates channel_id's standup data (key to new value)
    '''
    this_channel = get_channel_data(channel_id, CHANNEL_DATA)
    this_channel['standup'][key] = value

def update_standup(channel_id, length, CHANNEL_DATA):
    '''
    Updates channel_id's 'standup' key with new standup time_finish
    Returns the time the standup finishes
    '''
    time_finish = datetime.now() + timedelta(seconds=length)

    update_standup_key(channel_id, 'is_active', 1, CHANNEL_DATA)
    update_standup_key(channel_id, 'time_finish', time_finish, CHANNEL_DATA)
    update_standup_key(channel_id, 'message', None, CHANNEL_DATA)
    return time_finish

def reset_standup(channel_id, CHANNEL_DATA):
    '''
    Resets channel_id's standup to default values
    Used to reset a standup once it is complete
    '''
    update_standup_key(channel_id, 'is_active', 0, CHANNEL_DATA)
    update_standup_key(channel_id, 'time_finish', None, CHANNEL_DATA)
    update_standup_key(channel_id, 'message', None, CHANNEL_DATA)

def is_message_valid(message):
    '''
    Determines if message <= 1000 characters
    Returns True if valid, False otherwise
    '''
    return len(message) <= 1000

'''
########## Main functions ##########
'''

def send_standup_later(token, length, channel_id, message, \
    USER_DATA, CHANNEL_DATA, MESSAGE_DATA):
    '''
    Sends standup message after time
    '''
    if not message is None:
        Timer(length, message_send(token, channel_id, message, \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA))
    reset_standup(channel_id, CHANNEL_DATA)


def standup_start(token, channel_id, length, USER_DATA, CHANNEL_DATA, MESSAGE_DATA):
    '''
    Starts the standup period for channel_id
    Returns time_finish
    InputError when the channel_id is not a valid channel_id
    InputError when a standup is currently in session
    '''
    if isValidUser('token', token, USER_DATA):
        # Errors
        if not is_valid_channel(channel_id, CHANNEL_DATA):
            raise InputError("NOT A VALID a valid channel")
        elif is_standup_in_session(channel_id, CHANNEL_DATA):
            raise InputError(f'An active standup is currently running in \
                this channel')
    else:
        # Start Standup, Update channel_data standup key
        time_finish = update_standup(channel_id, length, CHANNEL_DATA)

        # Send message, reset standup data after length seconds
        message = get_standup_data(channel_id, CHANNEL_DATA)['message']
        if not message is None:
            send_standup_later(token, length, channel_id, message, \
                USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    return {'time_finish': time_finish.strftime('%Y %m %d %H %M %S')}


def standup_active(token, channel_id, USER_DATA, CHANNEL_DATA):
    '''
    Returns standup information
    InputError when the channel_id is not a valid channel_id
    '''
    if isValidUser('token', token, USER_DATA):
        if not is_valid_channel(channel_id, CHANNEL_DATA):
            raise InputError(f'{channel_id} is not a valid channel')
        else:
            channel_data = get_channel_data(channel_id, CHANNEL_DATA)['standup']
            channel_data_time = channel_data['time_finish']
            time_finish = None
            if not channel_data_time is None:
                time_finish = channel_data_time.strftime('%Y %m %d %H %M %S')
            is_active = channel_data['is_active']
    return {'is_active': is_active, 'time_finish': time_finish}

def standup_send(token, channel_id, message, USER_DATA, CHANNEL_DATA):
    '''
    Sends a message to the standup queue
    InputError when the channel_id or message not valid, standup in session
    AccessError when authorised user not a member of the channel
    '''
    if isValidUser('token', token, USER_DATA):
        if not is_valid_channel(channel_id, CHANNEL_DATA):
            raise InputError(f'{channel_id} is not a valid channel')
        elif not is_standup_in_session(channel_id, CHANNEL_DATA):
            raise InputError(f'An active standup is not currently running in \
                this channel')
        elif not is_message_valid(message):
            raise InputError('Message is more than 1,000 characters')
        elif not is_user_in_channel(token, channel_id, CHANNEL_DATA, USER_DATA):
            raise AccessError('The authorised user is not a member of the '
                              'channel that the message is within')
    else:
        # Send standup message
        this_channel = get_channel_data(channel_id, CHANNEL_DATA)
        first_name = queryUserData('token', token, USER_DATA)['name_first']
        new_message = f"{first_name} {message} \n"
        if not this_channel['standup']['message'] is None:
            new_message = this_channel['standup']['message'] + new_message
        update_standup_key(channel_id, 'message', new_message, CHANNEL_DATA)
    return {}


def search(token, query_str, USER_DATA, MESSAGE_DATA):
    '''
    returns a list of all messages sent by user in cronological order
    assuming list of messages is kept in most recent first
    '''
    message_list = {'message':[]}
    result = queryUserData('token', token, USER_DATA)
    u_id = result['u_id'] 
    for chan in MESSAGE_DATA['channels']:
        for me in chan['messages']:
            if me['u_id'] == u_id:
                if query_str in me['message']:
                    message_list['message'].append({
                        'message' : me['message'],
                    })
    return message_list

def usersAll(token, USER_DATA):     # pylint: disable=invalid-name
    '''
    Returns a list of all users and their associated details.
    '''
    if isValidUser('token', token, USER_DATA):
        all_users = {'users': []}

        # Removes sensitive data before returning
        for usr in USER_DATA['users']:
            if usr['email'] == '':
                continue

            # Ensures only relavant data is passed on
            all_users['users'].append({'u_id': usr['u_id'],
                                       'email': usr['email'],
                                       'name_first': usr['name_first'],
                                       'name_last': usr['name_last'],
                                       'handle_str': usr['handle_str']
                                       })

    else:
        raise AccessError('Invalid token!')

    return all_users


def admin_userpermission_change(token, u_id, permission_id, USER_DATA):     # pylint: disable=invalid-name
    '''
    Allows a owner to change the permission_id of other users, making them
    owners or regular members
    '''
    # Checks token and u_id are valid
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    if not isValidUser('u_id', u_id, USER_DATA):
        raise InputError(description='Invalid user ID!')

    # Checks permission_id is valid and usr1 is authorised
    if permission_id < 1 or permission_id > 2:
        raise InputError(description='Invalid permission ID!')

    usr1 = queryUserData('token', token, USER_DATA)
    if usr1['permission_id'] != 1:
        raise AccessError(description='Unauthorised user!')

    # Collects and adjusts usr2 of u_id's permission_id
    usr2 = queryUserData('u_id', u_id, USER_DATA)
    usr2['permission_id'] = permission_id

    return{}


def admin_user_remove(token, u_id, USER_DATA):      # pylint: disable=invalid-name
    '''
    Allows a owner to delete a user. The deleted user will have its email and
    password remove along with its name and handle changed to 'Deleted' but its
    messages will still be visible
    '''
    # Checks token and u_id are valid
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    if not isValidUser('u_id', u_id, USER_DATA):
        raise InputError(description='Invalid user ID!')

    # Checks user hasn't already been deleted
    usr2 = queryUserData('u_id', u_id, USER_DATA)
    if usr2['password'] == '' and usr2['email'] == '':
        raise InputError(description='Invalid user ID!')

    # Checks usr1 is authorised
    usr1 = queryUserData('token', token, USER_DATA)
    if usr1['permission_id'] != 1:
        raise AccessError(description='Unauthorised user!')

    # Changes usr2's details
    usr2['email'] = ''
    usr2['password'] = ''
    usr2['token'] = -1
    usr2['reset_code'] = -1
    usr2['permission_id'] = 0
    usr2['name_first'] = '[deleted]'
    usr2['name_last'] = ''
    usr2['handle_str'] = '[deleted]'

    return {}
