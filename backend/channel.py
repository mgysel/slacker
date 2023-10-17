'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  24/03/2020
Description:    Invite, details, messages, leave, join, addowner and removeowner
                functions for slackr
'''
from error import AccessError, InputError
from helpers import queryUserData, isValidUser
from objects.channelObject import Channel
from objects.userObject import User
from objects.messageObject import Message
from helpers import get_profile_img_url

'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def channel_invite(token, channel_id, u_id):   # pylint: disable=invalid-name
    '''
    Adds a user of u_id to a channel immediately after invitation
    '''
    # Check valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Get channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError('Invalid channel ID!')

    # Check user is a member of channel
    authorised_user = False
    for member in channel['members']:
        if user['u_id'] == member['u_id']:
            authorised_user = True
            break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not member of channel!')

    # Checks user to be invited is valid
    user = User.find_user_by_attribute('u_id', u_id)
    if user is None:
        raise InputError(description='Invalid user entered!')

    # Adds user to channel at rank 0 (i.e. simply a channel member) if
    # not already a member, else does nothing

    # If owner of slackr, makes them channel owner
    if user['permission_id'] == 1:
        new_member = {'u_id': u_id, 'rank': 1}
    else:
        new_member = {'u_id': u_id, 'rank': 0}

    if new_member not in channel['members']:
        Channel.push_channel_attribute('channel_id', channel_id, 'members', new_member)

    return {}

def channel_details(token, channel_id):    # pylint: disable=invalid-name
    '''
    Returns channel details including channel name and id, along with
    owner_members and regular members. Only given to members of the channel
    '''
    # Check valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')

    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    # Check user is a member of channel
    authorised_user = False
    for member in channel['members']:
        if user['u_id'] == member['u_id']:
            authorised_user = True
            break
    if not authorised_user:
        raise AccessError(description='Unauthorised user, you must to a member to view details!')

    # Begins gathering relevant channel details
    details = {'name': channel['name'], 'owner_members': [], 'all_members': []}

    for member in channel['members']:
        user = User.find_user_by_attribute('u_id', member['u_id'])
        if user is None:
            continue

        # Looks for owners to add to owner_members
        mem_details = {
            'u_id': user['u_id'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'profile_img_url': get_profile_img_url(user['profile_img_url'])
        }
        if member['rank']:
            details['owner_members'].append(mem_details)
        details['all_members'].append(mem_details)

    return details

def channel_messages(token, channel_id, start):      # pylint: disable=invalid-name, too-many-arguments, too-many-branches
    '''
    Returns recent 50 messages from specified start for the given channel.
    if less than 50 messages left returns all left
    '''
    # Checks user and channel are both valid, and collects data on both
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')

    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    # Checks user is a member of channel
    authorised_user = False
    for member in channel['members']:
        if user['u_id'] == member['u_id']:
            authorised_user = True
            break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not member of channel!')

    # Collects channels message data, if nothing returns empty message list
    messages = Message.find_messages_by_attribute('channel_id', channel_id)
    if len(messages) == 0:
        if start > 0:
            raise InputError(description='Invalid start enter, larger than number of messages!')

        return {
            'messages': [],
            'start': 0,
            'end': -1,
            }

    # Checks start is not larger than total messages
    if start >= len(messages):
        raise InputError(description='Invalid start enter, larger than number of messages!')

    # Determines when to stop collecting messages
    end = start + 50

    if end > (len(messages) - 1):
        end = -1

    # Makes variable and collects messages
    msgs = {'messages': [], 'start': start, 'end': end}

    # If end = -1 returns messaged from 'start' to end of list
    if end == -1:
        for message in messages[start:]:
            del message['_id']
            for react in message['reacts']:
                if user['u_id'] in react['u_ids']:
                    react['is_this_user_reacted'] = True
                else:
                    react['is_this_user_reacted'] = False
            msgs['messages'].append(message)
    else:
        for message in messages[start:end]:
            del message['_id']
            for react in message['reacts']:
                if user['u_id'] in react['u_ids']:
                    react['is_this_user_reacted'] = True
                else:
                    react['is_this_user_reacted'] = False
            msgs['messages'].append(message)

    msgs['messages'] = sorted(msgs['messages'], key=lambda h: (h['is_pinned'], h['time_created']))
    return msgs

def channel_leave(token, channel_id):      # pylint: disable=invalid-name
    '''
    Removes a user from a channel at their own discretion
    '''
    # Checks user and channel are both valid
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')

    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    # Trys removing user from channel, if not found gives AccessError
    user_found = False
    user_num = 0
    for member in channel['members']:
        if member['u_id'] == user['u_id']:
            del channel['members'][user_num]
            Channel.update_channel_attribute('channel_id', channel_id, 'members', channel['members'])
            user_found = True
            break
        user_num = user_num + 1

    if not user_found:
        raise AccessError(description='Unauthorised user, not in channel!')

    return {}

def channel_join(token, channel_id):       # pylint: disable=invalid-name
    '''
    Adds a user to a channel if they are authorised to join
    '''
    # Checks token, then collects user data
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')
    
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    if not channel['is_public']:
        if user['permission_id'] == 2:
            raise AccessError(description='Channel is private!')

    # Adds user to channel as rank 0 (i.e. simply a channel member) if
    # already in channel does nothing

    # If owner of slackr, makes them channel owner
    if user['permission_id'] == 1:
        new_member = {'u_id': user['u_id'], 'rank': 1}
    else:
        new_member = {'u_id': user['u_id'], 'rank': 0}

    if new_member not in channel['members']:
        channel['members'].append(new_member)
        Channel.push_channel_attribute('channel_id', channel_id, 'members', new_member)

    return {}

def channel_addowner(token, channel_id, u_id):     # pylint: disable=invalid-name, too-many-branches
    '''
    Makes a user an owner of a channel, if the user calling the
    function is authorised
    '''
    # Checks token, then collects user data
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')

    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling removeowner is a owner of channel or slackr owner
    authorised_user = False
    for member in channel['members']:
        if user['u_id'] == member['u_id'] or user['permission_id'] == 1:
            if member['rank'] or user['permission_id'] == 1:
                authorised_user = True
                break
    if not authorised_user:
        raise AccessError(description='Unauthorised user, not owner of channel!')

    is_owner = False
    for member in channel['members']:
        if u_id == member['u_id']:
            if member['rank']:
                is_owner = True
                break
            else:
                member['rank'] = 1
                Channel.update_channel_attribute('channel_id', channel_id, 'members', channel['members'])
                return {}
    
    if is_owner:
        raise InputError(description='User is already a owner of channel!')

    # If user isn't a member then adds them to channel as owner
    new_member = {'u_id': user['u_id'], 'rank': 1}
    Channel.push_channel_attribute('channel_id', channel_id, 'members', new_member)

    return {}

def channel_removeowner(token, channel_id, u_id):      # pylint: disable=invalid-name
    '''
    Demotes owner of channel with u_id, if the user calling the function
    is authorised
    '''
    # Checks token, then collects user data
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError(description='Invalid token!')
    
    user2 = User.find_user_by_attribute('u_id', u_id)
    if user2 is None:
        raise InputError(description='Invalid user ID!')
    
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling removeowner is an owner of channel or owner of slackr
    authorised_user = False
    for member in channel['members']:
        if user['u_id'] == member['u_id'] or user['permission_id'] == 1:
            if member['rank'] or user['permission_id'] == 1:
                authorised_user = True
                break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not owner of channel!')

    owner_user = False
    for member in channel['members']:
        if u_id == member['u_id']:
            if member['rank']:
                owner_user = True
                if user2['permission_id'] == 1:
                    raise AccessError(description='Owners of slackr can not be demoted!')
                # Demotes user to regular member
                member['rank'] = 0
                Channel.update_channel_attribute('channel_id', channel_id, 'members', channel['members'])
                break

    if not owner_user:
        raise InputError(description='User not owner of channel!')

    return {}

'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def get_channel_data(channel_id):     # pylint: disable=invalid-name
    '''
    Returns data on a channel given its channel_id. If no such channel exists
    returns an empty dictionary. 
    '''
    # Get channel with channel_id
    channel_output = {}
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is not None:
        channel_output = {
            'channel_id': channel['channel_id'],
            'name': channel['name'],
            'is_public': channel['is_public'],
            'members': channel['members'],
            'messages': channel['messages']
        }

    return channel_output

def get_message_data(channel_id):     # pylint: disable=invalid-name
    '''
    Returns message data on a channel given its channel_id. If no such data
    exists returns an empty dictionary. Note data edited from this is also
    edited in MESSAGE_DATA.
    '''
    # Get channel with channel_id
    messages = []
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is not None:
        messages = reversed(channel['messages'])

    return messages