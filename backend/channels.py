'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Profile, Set Name, Set Email, Set Handle functions for slackr
'''
from error import AccessError, InputError
from helpers import queryUserData, isValidUser


'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def is_valid_name(channel_name):
    '''
    Returns True if channel_name <= 20 characters
    Returns False otherwise
    '''
    return len(channel_name) <= 20


'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def channels_list(token, CHANNEL_DATA, USER_DATA):      # pylint: disable=invalid-name
    '''
    Provides a list of all channels that authorised user is a part of
    '''
    if isValidUser('token', token, USER_DATA):
        # Determine user_id from token
        u_id = queryUserData('token', token, USER_DATA).get('u_id')

        # Append each channel u_id is a part of
        user_channels = []
        # Loop through channels
        for channel in CHANNEL_DATA['channels']:
            # Loop through members
            for member in channel['members']:
                if member['u_id'] == u_id:
                    user_channels.append(channel)

        chnnls_list = {'channels': []}
        for channel in user_channels:
            chnnls_list['channels'].append({
                'channel_id': channel['channel_id'],
                'name': channel['name']
                })
    else:
        raise AccessError('Invalid token!')

    return chnnls_list


def channels_listall(token, CHANNEL_DATA, USER_DATA):   # pylint: disable=invalid-name
    '''
    Provides a list of all channels and their details
    '''
    if not isValidUser('token', token, USER_DATA):
        raise AccessError('Invalid token!')

    channels = {'channels': []}
    for chnnl in CHANNEL_DATA['channels']:
        channels['channels'].append({
                        'channel_id': chnnl['channel_id'],
                        'name': chnnl['name']
                        })

    return channels


def channels_create(token, name, is_public, CHANNEL_DATA, USER_DATA):   # pylint: disable=invalid-name
    '''
    Creates a new channel with name, that is public or private
    Returns {channel_id} when no errors
    Returns InputError when name is more than 20 characters
    '''
    if isValidUser('token', token, USER_DATA):
        if is_valid_name(name):
            # Create new channel
            # Rank 1 means owner, 0 meaning user
            rank = 1
            num_members = 1
            u_id = queryUserData('token', token, USER_DATA)['u_id']

            new_channel = {
                'channel_id': CHANNEL_DATA['num_channels'],
                'name': name,
                'is_public': is_public,
                'num_members': num_members,
                'members':
                    [{'u_id': u_id, 'rank': rank}],
                'standup': {'is_active': 0, 'time_finish': None, 'message': None}
                }

            # Update CHANNEL_DATA
            CHANNEL_DATA['channels'].append(new_channel)
            CHANNEL_DATA['num_channels'] = CHANNEL_DATA['num_channels'] + 1

        else:
            # InputError if name not valid
            raise InputError('Name is more than 20 characters long.')
    else:
        raise AccessError('Invalid token!')

    return {'channel_id': new_channel['channel_id']}
