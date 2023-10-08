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
from objects.userObject import User
from objects.channelObject import Channel
from objects.messageObject import Message
import sched
import time
import os

'''
########## Helper functions ##########
'''

def is_message_valid(message):
    '''
    Determines if message <= 1000 characters
    Returns True if valid, False otherwise
    '''
    return len(message) <= 1000

'''
########## Main functions ##########
'''

def standup_start(token, channel_id, length):
    '''
    Starts the standup period for channel_id
    Returns time_finish
    InputError when the channel_id is not a valid channel_id
    InputError when a standup is currently in session
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    # Check if valid channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError('Invalid channel ID!')
    
    # Check if standup is in session
    if channel['standup']['is_active']:
        raise InputError('An active standup is currently running in this channel')
    
    # Update channel standup
    time_finish = datetime.now() + timedelta(seconds=length)
    standup_obj = {
        'is_active': 1,
        'time_finish': time_finish,
        'message': None
    }
    Channel.update_channel_attribute('channel_id', channel_id, 'standup', standup_obj)

    Timer(length, standup_end, [token, channel_id]).start()

    return {'time_finish': time_finish.strftime('%Y %m %d %H %M %S')}

def standup_end(token, channel_id):
    '''
    Ends the standup period for channel_id
    '''
    # Get user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Get channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError('Invalid channel ID!')
    
    # Send standup message
    if channel['standup']['message'] is not None:
        message_send(token, channel_id, channel['standup']['message'])

    # Update standup
    channel_standup = {
        'is_active': 0,
        'time_finish': None,
        'message': None
    }
    Channel.update_channel_attribute('channel_id', channel_id, 'standup', channel_standup)
    
def standup_active(token, channel_id):
    '''
    Returns standup information
    InputError when the channel_id is not a valid channel_id
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    # Check if valid channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError('Invalid channel ID!')

    channel_data_time = channel['standup']['time_finish']
    time_finish = None
    if channel_data_time is not None:
        time_finish = channel_data_time.timestamp()
    is_active = channel['standup']['is_active']
    
    return {'is_active': is_active, 'time_finish': time_finish}

def standup_send(token, channel_id, message):
    '''
    Sends a message to the standup queue
    InputError when the channel_id or message not valid, standup in session
    AccessError when authorised user not a member of the channel
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    # Check if valid channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError('Invalid channel ID!')
    
    # Check if standup is in session
    if not channel['standup']['is_active']:
        raise InputError('An active standup is not currently running in this channel')
    
    # Check if message is valid
    if not is_message_valid(message):
        raise InputError('Message is more than 1,000 characters')
    
    # Check if user is in channel
    is_member = False
    for member in channel['members']:
        if member['u_id'] == user['u_id']:
            is_member = True
            break
    if not is_member:
        raise AccessError('The authorised user is not a member of the channel that the message is within')

    # Send standup message
    new_message = f"{user['handle_str']}: {message}.\n"
    channel_standup = channel['standup']
    if channel_standup['message'] is not None:
        new_message = channel_standup['message'] + new_message
    Channel.update_channel_attribute('channel_id', channel_id, 'standup', {'is_active': channel_standup['is_active'], 'time_finish': channel_standup['time_finish'], 'message': new_message})

    return {}

def search(token, query_str):
    '''
    returns a list of all messages sent by user in chronological order
    assuming list of messages is kept in most recent first
    '''
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    messages = Message.find_messages_by_attribute('u_id', user['u_id'])
    messages_list = []
    for m in messages:
        if query_str.lower() in m['message'].lower():
            del m['_id']
            messages_list.append(m)

    print("MESSAGES LIST: ", messages_list)
    return {
        'messages': messages_list
    }

def usersAll(token):     # pylint: disable=invalid-name
    '''
    Returns a list of all users and their associated details.
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    all_users = {'users': []}
    users = User.get_all_users()

    # Removes sensitive data before returning
    for user in users:
        all_users['users'].append({
            'u_id': user.u_id,
            'name_first': user.name_first,
            'name_last': user.name_last,
            'handle_str': user.handle_str,
            'profile_img_url': user.profile_img_url,
            'permission_id': user.permission_id,
        })

    return all_users

def admin_userpermission_change(token, u_id, permission_id):     # pylint: disable=invalid-name
    '''
    Allows a owner to change the permission_id of other users, making them
    owners or regular members
    '''
    # Checks token and u_id are valid
    user1 = User.find_user_by_attribute('token', token)
    if user1 is None:
        raise AccessError(description='Invalid token!')
    if user1['permission_id'] != 1:
        raise AccessError(description='Unauthorised user!')
    
    user2 = User.find_user_by_attribute('u_id', u_id)
    if user2 is None:
        raise InputError(description='Invalid user ID!')

    # Checks permission_id is valid and usr1 is authorised
    if permission_id < 1 or permission_id > 3:
        raise InputError(description='Invalid permission ID!')

    # Collects and adjusts usr2 of u_id's permission_id
    User.update_user_attribute('u_id', u_id, 'permission_id', permission_id)

    return{}

def admin_user_remove(token, u_id):      # pylint: disable=invalid-name
    '''
    Allows a owner to delete a user. The deleted user will have its email and
    password remove along with its name and handle changed to 'Deleted' but its
    messages will still be visible
    '''
    # Checks token and u_id are valid
    user1 = User.find_user_by_attribute('token', token)
    if user1 is None:
        raise AccessError(description='Invalid token!')
    
    user2 = User.find_user_by_attribute('u_id', u_id)
    if user2 is None:
        raise InputError(description='Invalid user ID!')

    # Checks user1 is authorised
    if user1['permission_id'] != 1:
        raise AccessError(description='Unauthorised user!')

   # Update database entry 
    user_attribute_updates = {
        'email': '',
        'password': '',
        'token': -1,
        'reset_code': -1,
        'permission_id': 0,
        'name_first': '[deleted]',
        'name_last': '',
        'handle_str': '[deleted]'
    }
    User.update_user_attributes('u_id', u_id, user_attribute_updates)

    file_type = user2['profile_img_url'].split(".")[-1]
    if os.path.exists(f'./static/{u_id}.{file_type}'):
        os.remove(f'./static/{u_id}.{file_type}')

    return {}
