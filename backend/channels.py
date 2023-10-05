'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Profile, Set Name, Set Email, Set Handle functions for slackr
'''
from error import AccessError, InputError
from helpers import queryUserData, isValidUser
from objects.userObject import User
from objects.channelObject import Channel


'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def channels_list(token):      # pylint: disable=invalid-name
    '''
    Provides a list of all channels that authorised user is a part of
    '''
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    channels_db = Channel.get_all_channels()
    channels = {'channels': []}
    for channel in channels_db:
        print("User id: ", user['_id'])
        print("Channel members: ", channel['members'])
        for member in channel['members']:
            if user['_id'] == member['u_id']:
                channels['channels'].append({
                    'channel_id': str(channel['_id']),
                    'name': channel['name']
                })
                break
        
    print("Channels user is in: ", channels)
    return channels

def channels_listall(token):   # pylint: disable=invalid-name
    '''
    Provides a list of all channels and their details
    '''
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    channels_db = Channel.get_all_channels()
    channels = {'channels': []}
    for channel in channels_db:
        channels['channels'].append({
            'channel_id': str(channel['_id']),
            'name': channel['name']
        })

    return channels

def channels_create(token, name, is_public):   # pylint: disable=invalid-name
    '''
    Creates a new channel with name, that is public or private
    Returns {channel_id} when no errors
    Returns InputError when name is more than 20 characters
    '''
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    if not is_valid_name(name):
        raise InputError('Name is more than 20 characters long.')

    # Create new channel
    rank = 1
    num_members = 1
    members = [{'u_id': user['_id'], 'rank': rank}]
    standup = {'is_active': 0, 'time_finish': None, 'message': None}

    # Insert channel to db
    channel = Channel(None, name, is_public, num_members, members, standup)
    channel_id = Channel.insert_one(channel)

    return {'channel_id': str(channel_id)}

'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def is_valid_name(channel_name):
    '''
    Returns True if channel_name <= 20 characters
    Returns False otherwise
    '''
    return len(channel_name) <= 20