'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  24/03/2020
Description:    Invite, details, messages, leave, join, addowner and removeowner
                functions for slackr
'''
from error import AccessError, InputError
from helpers import queryUserData, isValidUser

'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def get_channel_data(channel_id, CHANNEL_DATA):     # pylint: disable=invalid-name
    '''
    Returns data on a channel given its channel_id. If no such channel exists
    returns an empty dictionary. Note data edited from this is also edited in
    CHANNEL_DATA
    '''
    channel = {}

    for chn in CHANNEL_DATA['channels']:
        if chn['channel_id'] == channel_id:
            channel = chn
            break

    return channel


def get_message_data(channel_id, MESSAGE_DATA):     # pylint: disable=invalid-name
    '''
    Returns message data on a channel given its channel_id. If no such data
    exists returns an empty dictionary. Note data edited from this is also
    edited in MESSAGE_DATA.
    '''
    messages = []

    for chn in MESSAGE_DATA['channels']:
        if chn['channel_id'] == channel_id:
            # Reverses data so most recent is first
            messages = list(reversed(chn['messages']))
            break

    return messages


'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def channel_invite(token, channel_id, u_id, CHANNEL_DATA, USER_DATA):   # pylint: disable=invalid-name
    '''
    Adds a user of u_id to a channel immediately after invitation
    '''
    # Checks token, then collects user data
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)

    # Checks channel is valid
    channel = get_channel_data(channel_id, CHANNEL_DATA)
    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling invite is member of channel
    authorised_user = False

    for member in channel['members']:
        if usr['u_id'] == member['u_id']:
            authorised_user = True
            break
    if not authorised_user:
        raise AccessError(description='Unauthorised user, not member of channel!')

    # Checks user to be invited is valid
    if not isValidUser('u_id', u_id, USER_DATA):
        raise InputError(description='Invalid user entered!')

    usr2 = queryUserData('u_id', u_id, USER_DATA)
    if usr2['email'] == '':
        raise InputError(description='Invalid user entered!')

    # Adds user to channel at rank 0 (i.e. simply a channel member) if
    # not already a member, else does nothing

    # If owner of slackr, makes them channel owner
    if usr2['permission_id'] == 1:
        new_member = {'u_id': u_id, 'rank': 1}
    else:
        new_member = {'u_id': u_id, 'rank': 0}

    if new_member not in channel['members']:
        channel['members'].append(new_member)

    return {}


def channel_details(token, channel_id, CHANNEL_DATA, USER_DATA):    # pylint: disable=invalid-name
    '''
    Returns channel details including channel name and id, along with
    owner_members and regular members. Only given to members of the channel
    '''
    # Checks token, then collects user data
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)

    # Checks channel is valid
    channel = get_channel_data(channel_id, CHANNEL_DATA)
    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling details is member of channel
    authorised_user = False

    for member in channel['members']:
        if usr['u_id'] == member['u_id']:
            authorised_user = True
            break
    if not authorised_user:
        raise AccessError(description='Unauthorised user, you must to a member to view details!')

    # Begins gathering relevant channel details
    details = {'name': channel['name'], 'owner_members': [], 'all_members': []}

    for member in channel['members']:
        # Ensures deleted users are not listed
        email = queryUserData('u_id', member['u_id'], USER_DATA)['email']
        if email == '':
            continue

        # Looks for owners to add to owner_members
        if member['rank']:
            mem_data = queryUserData('u_id', member['u_id'], USER_DATA)
            mem_details = {'u_id': mem_data['u_id'], \
                            'name_first': mem_data['name_first'], \
                            'name_last': mem_data['name_last']}
            details['owner_members'].append(mem_details)

        # Adds all members to all_members
        mem_data = queryUserData('u_id', member['u_id'], USER_DATA)
        mem_details = {'u_id': mem_data['u_id'], \
                        'name_first': mem_data['name_first'], \
                        'name_last': mem_data['name_last']}
        details['all_members'].append(mem_details)

    return details


def channel_messages(token, channel_id, start, CHANNEL_DATA, MESSAGE_DATA, USER_DATA):      # pylint: disable=invalid-name, too-many-arguments, too-many-branches
    '''
    Returns recent 50 messages from specified start for the given channel.
    if less than 50 messages left returns all left
    '''
    # Checks user and channel are both valid, and collects data on both
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)
    channel = get_channel_data(channel_id, CHANNEL_DATA)

    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Checks user is a member of channel
    authorised_user = False
    for member in channel['members']:
        if usr['u_id'] == member['u_id']:
            authorised_user = True
            break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not member of channel!')

    # Collects channels message data, if nothing returns empty message list
    messages = get_message_data(channel_id, MESSAGE_DATA)

    if messages == []:
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
            msgs['messages'].append(message)
    else:
        for message in messages[start:end]:
            msgs['messages'].append(message)

    return msgs


def channel_leave(token, channel_id, CHANNEL_DATA, USER_DATA):      # pylint: disable=invalid-name
    '''
    Removes a user from a channel at their own discretion
    '''
    # Checks user and channel are both valid
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)
    channel = get_channel_data(channel_id, CHANNEL_DATA)

    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Trys removing user from channel, if not found gives AccessError
    user_found = False
    user_num = 0
    for member in channel['members']:
        if member['u_id'] == usr['u_id']:
            del channel['members'][user_num]
            user_found = True
            break
        user_num = user_num + 1

    if not user_found:
        raise AccessError(description='Unauthorised user, not in channel!')

    return {}


def channel_join(token, channel_id, CHANNEL_DATA, USER_DATA):       # pylint: disable=invalid-name
    '''
    Adds a user to a channel if they are authorised to join
    '''
    # Checks token, then collects user data
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)

    # Checks channel is valid and public
    channel = get_channel_data(channel_id, CHANNEL_DATA)
    if channel == {}:
        raise InputError(description='Invalid channel ID!')
    if not channel['is_public']:
        if usr['permission_id'] == 2:
            raise AccessError(description='Channel is private!')

    # Adds user to channel as rank 0 (i.e. simply a channel member) if
    # already in channel does nothing

    # If owner of slackr, makes them channel owner
    if usr['permission_id'] == 1:
        new_member = {'u_id': usr['u_id'], 'rank': 1}
    else:
        new_member = {'u_id': usr['u_id'], 'rank': 0}

    if new_member not in channel['members']:
        channel['members'].append(new_member)

    return {}


def channel_addowner(token, channel_id, u_id, CHANNEL_DATA, USER_DATA):     # pylint: disable=invalid-name, too-many-branches
    '''
    Makes a user an owner of a channel, if the user calling the
    function is authorised
    '''
    # Checks token, then collects user data
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)

    # Checks channel is valid
    channel = get_channel_data(channel_id, CHANNEL_DATA)
    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling removeowner is a owner of channel or slackr owner
    authorised_user = False
    for member in channel['members']:
        if usr['u_id'] == member['u_id'] or usr['permission_id'] == 1:
            if member['rank'] or usr['permission_id'] == 1:
                authorised_user = True
                break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not owner of channel!')

    # Checks user, to be added as owner, is valid then collects users data
    # Then checks if they are a channel member, then gives owner rank
    if not isValidUser('u_id', u_id, USER_DATA):
        raise InputError(description='Invalid u_id!')
    new_owner = queryUserData('u_id', u_id, USER_DATA)

    is_owner = False
    for member in channel['members']:
        if new_owner['u_id'] == member['u_id']:
            if member['rank']:
                is_owner = True
                break
            else:
                member['rank'] = 1
                break

    if is_owner:
        raise InputError(description='User is already a owner of channel!')

    # If user isn't a member then adds them to channel as owner
    new_member = {'u_id': new_owner['u_id'], 'rank': 1}
    if new_member not in channel['members']:
        channel['members'].append(new_member)

    return {}


def channel_removeowner(token, channel_id, u_id, CHANNEL_DATA, USER_DATA):      # pylint: disable=invalid-name
    '''
    Demotes owner of channel with u_id, if the user calling the function
    is authorised
    '''
    # Checks token, then collects user data
    if not isValidUser('token', token, USER_DATA):
        raise AccessError(description='Invalid token!')

    usr = queryUserData('token', token, USER_DATA)

    # Checks channel is valid
    channel = get_channel_data(channel_id, CHANNEL_DATA)
    if channel == {}:
        raise InputError(description='Invalid channel ID!')

    # Checks user calling removeowner is a owner of channel or owner of slackr
    authorised_user = False
    for member in channel['members']:
        if usr['u_id'] == member['u_id'] or usr['permission_id'] == 1:
            if member['rank'] or usr['permission_id'] == 1:
                authorised_user = True
                break

    if not authorised_user:
        raise AccessError(description='Unauthorised user, not owner of channel!')

    # Checks user to be removed from owner is valid then collects users data
    # Then checks if they are a channel owner, if true then removes their rank
    if not isValidUser('u_id', u_id, USER_DATA):
        raise InputError(description='Invalid u_id!')

    usr_owner = queryUserData('u_id', u_id, USER_DATA)

    owner_user = False
    for member in channel['members']:
        if usr_owner['u_id'] == member['u_id']:
            if member['rank']:
                owner_user = True
                if usr_owner['permission_id'] == 1:
                    raise AccessError(description='Owners of slackr can not be demoted!')
                # Demotes user to regular member
                member['rank'] = 0
                break

    if not owner_user:
        raise InputError(description='User not owner of channel!')

    return {}
