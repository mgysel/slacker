'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Message functions for slackr
'''

import time
import sched
from error import AccessError, InputError
from helpers import queryUserData
from random_word import RandomWords
from objects.channelObject import Channel
from objects.userObject import User
from objects.messageObject import Message

def message_send(token, channel_id, message): # pylint: disable=invalid-name,too-many-arguments,too-many-locals,too-many-branches
    '''
    Sends a message to a valid channel
    '''
    # Checking valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # checking message has no more than 1k chars
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Checking that the channel_id is valid
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError("Channel ID is invalid")

    # Getting user's u_id
    u_id = user['u_id']

    # Checking that user has joined the channel they are trying to post to
    joined_channel = 0
    for i in channel['members']:
        if i['u_id'] == u_id:
            joined_channel = 1
            break

    if joined_channel == 0:
        raise AccessError("The authorised user has not joined the channel \
            they are trying to post to")
    
    # # Call hangman function 
    # if message == "/hangman" or message.startswith("/guess") is True:
    #     hangman(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)

    message_id = -1
    time_stamp = int(time.time())
    reacts = []
    is_pinned = False
    message = Message(None, message_id, u_id, channel_id, message, time_stamp, reacts, is_pinned)
    _id = Message.insert_one(message)
    if _id is None:
        raise InputError("Message could not be added to database")
    
    message = Message.find_message_by_attribute('_id', _id)
    if message is None:
        raise InputError("Message could not be retrieved from database")

    return {
        'message_id': message['message_id']
    }

def message_remove(token, message_id): # pylint: disable=invalid-name,too-many-branches
    '''
    Removes a message that has already been sent
    '''
    # Checking that the token belong to a valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    u_id = user['u_id']

    # Checking that message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")
    
    # Checking channel
    channel_id = message['channel_id']
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError("Channel ID of message is invalid")

    is_owner = 0
    for i in channel['members']:
        if i['u_id'] == u_id and i['rank'] == 1:
            is_owner = 1
            break

    sent_by = 0
    if message['u_id'] == u_id:
        sent_by = 1

    if sent_by != 1 and is_owner != 1:
        raise AccessError("Cannot remove: User did not send the message \
            and user is not an owner of the channel")
    
    Message.delete_message_by_attribute('message_id', message_id)

    return {}

def message_edit(token, message_id, msg): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Edits a message that has already been sent
    '''
    '''
    Removes a message that has already been sent
    '''
    # Checking that the token belong to a valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    u_id = user['u_id']

    # Checking that message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")
    
    # Checking channel
    channel_id = message['channel_id']
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError("Channel ID of message is invalid")

    sent_by = 0
    if message['u_id'] == u_id:
        sent_by = 1

    if sent_by != 1:
        raise AccessError("Cannot edit: User did not send the message \
            and user is not an owner of the channel")
    
    Message.update_message_attribute('message_id', message_id, 'message', msg)

    return {}

def send_later(u_id, channel_id, message): # pylint: disable=invalid-name,unused-argument,too-many-arguments
    '''
    Send a message at a later time specified
    '''
    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Add message 
    m_id = -1
    u_id = u_id
    message = message
    time_created = time_stamp
    reacts = []
    is_pinned = False

    new_message = Message(None, m_id, u_id, channel_id, message, time_created, reacts, is_pinned)
    _id = Message.insert_one(new_message)
    if _id is None:
        raise InputError("Message could not be added to database")

    message = Message.find_message_by_attribute('_id', _id)

    return {
        'message_id': message['message_id']
    }

def message_sendlater(token, channel_id, message, time_sent): # pylint: disable=invalid-name,too-many-arguments
    '''
    Send a message at a later time specified
    '''
    print("Sending message later")
    print("Time sent: ", time_sent)
    # Check valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    # Check valid channel
    channel = Channel.find_channel_by_attribute('channel_id', channel_id)
    if channel is None:
        raise InputError("Channel ID is invalid")
    
    # Check user a member of channel
    is_member = 0
    for i in channel['members']:
        if i['u_id'] == user['u_id']:
            is_member = 1
            break
    if is_member == 0:
        raise AccessError("User is not a member of the channel that the message is within")

    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Checking that time_sent is not in the past
    if time_sent < time_stamp:
        raise InputError("Time sent is a time in the past")

    # checking message has no more than 1k chars
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Set up scheduler
    S = sched.scheduler(time.time, time.sleep)
    # Schedule when you want the action to occur
    S.enterabs(time_sent, 0, send_later, argument=(user['u_id'], channel_id, message))
    # Block until the action has been run
    S.run()

def message_react(token, message_id, react_id): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Allows the user to react to a specific message
    '''
    print("*** Inside message_react")
    print("Message id: ", message_id)
    print("React id: ", react_id)
    if react_id != 1:
        raise InputError("Not a valid react_id. The only valid react ID the frontend has is 1")

    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Check if message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    print("Message: ", message)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")

    # Get channel from message channel_id 
    channel = Channel.find_channel_by_attribute('channel_id', message['channel_id'])
    if channel is None:
        raise InputError("Channel ID of message is invalid")
    
    # Check that user is a member of the channel
    is_member = 0
    for i in channel['members']:
        if i['u_id'] == user['u_id']:
            is_member = 1
            break
    if is_member == 0:
        raise AccessError("User is not a member of the channel that the message is within")

    # Check if already reacted to message 
    react_exists = 0
    new_reacts = message['reacts']
    for react in new_reacts:
        if react_id == react['react_id']:
            if user['u_id'] in react['u_ids']:
                raise InputError("Message already reacted to by uid")
            else:
                react_exists = 1
                react['u_ids'].append(user['u_id'])
                break
    
    if react_exists == 0:
        new_reacts.append({
            'react_id': react_id,
            'u_ids': [user['u_id']],
        })

    # Adding the react 
    Message.update_message_attribute('message_id', message_id, 'reacts', new_reacts)

    return {}

def message_unreact(token, message_id, react_id): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Allows a user to unreact to a message
    '''
    print("REACT ID: ", react_id)
    if react_id != 1:
        raise InputError("Not a valid react_id. The only valid react ID the frontend has is 1")

    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Check if message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")

    # Get channel from message channel_id 
    channel = Channel.find_channel_by_attribute('channel_id', message['channel_id'])
    if channel is None:
        raise InputError("Channel ID of message is invalid")
    
    # Check that user is a member of the channel
    is_member = 0
    for i in channel['members']:
        if i['u_id'] == user['u_id']:
            is_member = 1
            break
    if is_member == 0:
        raise AccessError("User is not a member of the channel that the message is within")
    
    # Check if already reacted to message 
    react_exists = 0
    new_reacts = message['reacts']
    for react in new_reacts:
        if react_id == react['react_id']:
            if user['u_id'] in react['u_ids']:
                react['u_ids'].remove(user['u_id'])
                react_exists = 1
                break
    if react_exists == 0:
        raise InputError("Message not reacted to by uid")

    # Removing the react 
    Message.update_message_attribute('message_id', message_id, 'reacts', new_reacts)

    return {}

def message_pin(token, message_id): # pylint: disable=invalid-name,too-many-branches
    '''
    Pins a particular message for visibility
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Check if message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")
    
    # Check that message is not pinned
    if message['is_pinned']:
        raise InputError("Message with ID message_id is already pinned")

    # Get channel from message channel_id 
    channel = Channel.find_channel_by_attribute('channel_id', message['channel_id'])
    if channel is None:
        raise InputError("Channel ID of message is invalid")
    
    # Check that user is owner of the channel
    is_owner = 0
    for i in channel['members']:
        if i['u_id'] == user['u_id'] and i['rank'] == 1:
            is_owner = 1
            break
    if is_owner == 0:
        raise AccessError("User is not an owner of the channel that the message is within")

    #pinning the message
    Message.update_message_attribute('message_id', message_id, 'is_pinned', True)

    return {}

def message_unpin(token, message_id): # pylint: disable=invalid-name,too-many-branches
    '''
    Unpins a particular message
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Check if message exists
    message = Message.find_message_by_attribute('message_id', message_id)
    if message is None:
        raise InputError("Message(based on ID) no longer exists")
    
    # Check that message is pinned
    if not message['is_pinned']:
        raise InputError("Message with ID message_id is not pinned")

    # Get channel from message channel_id 
    channel = Channel.find_channel_by_attribute('channel_id', message['channel_id'])
    if channel is None:
        raise InputError("Channel ID of message is invalid")
    
    # Check that user is owner of the channel
    is_owner = 0
    for i in channel['members']:
        if i['u_id'] == user['u_id'] and i['rank'] == 1:
            is_owner = 1
            break
    if is_owner == 0:
        raise AccessError("User is not an owner of the channel that the message is within")

    # unpinning the message
    Message.update_message_attribute('message_id', message_id, 'is_pinned', False)

    return {}
