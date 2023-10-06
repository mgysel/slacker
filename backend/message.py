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


def hangman(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA):

    HANGMAN = [
    """
    _________
        |/        
        |              
        |                
        |                 
        |               
        |                   
        |___                 
        """,

    """
    _________
        |/   |      
        |              
        |                
        |                 
        |               
        |                   
        |___                 
        H""",

    """
    _________       
        |/   |              
        |   (_)
        |                         
        |                       
        |                         
        |                          
        |___                       
        HA""",

    """
    ________               
        |/   |                   
        |   (_)                  
        |    |                     
        |    |                    
        |                           
        |                            
        |___                    
        HAN""",

    """
    _________             
        |/   |               
        |   (_)                   
        |   /|                     
        |    |                    
        |                        
        |                          
        |___                          
        HANG""",

    """
    _________              
        |/   |                     
        |   (_)                     
        |   /|\                    
        |    |                       
        |                             
        |                            
        |___                          
        HANGM""",

    """
    ________                   
        |/   |                         
        |   (_)                      
        |   /|\                             
        |    |                          
        |   /                            
        |                                  
        |___                              
        HANGMA""",

    """
    ________
        |/   |     
        |   (_)    
        |   /|\           
        |    |        
        |   / \        
        |               
        |___           
        HANGMAN"""]

    # If command is /hangman
    if message == "/hangman":

        channelexists_flag = 0
        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                channelexists_flag = 1
                break

        # If the game has not yet started
        if channelexists_flag == 0:
            new_game = {
                'channel_id': channel_id,
                'word': "",
                'guessed_word': "",
                'wrong': 0,
                'guesses': [],
            }
            HANGMAN_DATA['channels'].append(new_game)

        # Setting up a new game
        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                # Set up game 
                if x['wrong'] == 0: 
                    r = RandomWords()
                    WORD = r.get_random_word(hasDictionaryDef="true", minLength=6)
                    WORD = WORD.upper()
                    x['word'] = WORD
                    x['guessed_word'] = "_ " * len(WORD)
                    x['wrong'] = 0
                    x['guesses'] = []
                    message_send(token, channel_id, "++++++++++ START OF ROUND ++++++++++")
                    message = HANGMAN[0]
                    message_send(token, channel_id, message)
                    message_send(token, channel_id, "Word is {}".format(x['guessed_word']))
                    message_send(token, channel_id, "You have used 0/7 Guesses")
                    message_send(token, channel_id, "To guess enter: '/guess X'")
                else: 
                    message_send(token, channel_id, "Game in progress. To guess enter: '/guess X'")
        
    if message.startswith("/guess") is True:
        
        channelexists_flag = 0
        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                channelexists_flag = 1
                break

        # If the game has not yet started
        if channelexists_flag == 0:
            message_send(token, channel_id, "You have not yet started a game. To start enter: '/hangman'")
        else:
            guess = message.split(" ")
            if len(guess) < 2:
                message_send(token, channel_id, "Invalid entry: to guess enter '/guess X'")
                return
            guess = guess[1]

        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                message_send(token, channel_id, "++++++++++ START OF ROUND ++++++++++")
                guess = guess.upper()
                x['guesses'].append(guess)

                # Checking correctness
                correct = 0
                if guess in x['word']:
                    correct = 1
                    HOLDER = ""
                    for i in range(len(x['word'])):
                        if x['word'][i] == guess:
                            HOLDER += guess
                        else:
                            HOLDER += x['guessed_word'][i]
                    x['guessed_word'] = HOLDER

                # Increment wrong counter if team does not guess correctly
                if correct == 0: 
                    x['wrong'] += 1

                WRONG = x['wrong']
                message = HANGMAN[WRONG]
                message_send(token, channel_id, message)
                message_send(token, channel_id, "WORD IS: {} \n".format(x['guessed_word']))
                message_send(token, channel_id, "YOU HAVE USED {}/7 LIVES: {}".format(WRONG, "X " * WRONG))
                message_send(token, channel_id, "YOU HAVE GUESSED THESE LETTERS/ WORDS: {}".format(x['guesses']))

                # check if the team has won
                if x['guessed_word'] == x['word']:
                    message_send(token, channel_id, "++++++++++ CONGRATULATIONS YOU WIN!!! THE WORD WAS {} ++++++++++".format(x['word']))
                    x['word'] = ""
                    x['guessed_word'] = ""
                    x['wrong'] = 0
                    x['guesses'] = []
                    x['in_progress'] = 0

                # check if the team has lost
                if x['wrong'] == 7:
                    message_send(token, channel_id, "{}".format(HANGMAN[7]))
                    message_send(token, channel_id, "YOU WERE HANGED. GAME OVER. THE WORD WAS {}".format(x['word']))
                    x['word'] = ""
                    x['guessed_word'] = ""
                    x['wrong'] = 0
                    x['guesses'] = []
                    x['in_progress'] = 0       
            break


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
    is_pinned = 0
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
    
    Message.update_message_attribute('message_id', message_id, 'message', msg)

    return {}

def send_later(u_id, channel_id, message, time_sent, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,unused-argument,too-many-arguments
    '''
    Send a message at a later time specified
    '''
    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Case 1: a dict has been created for that channel
    channel_exists_flag = 0
    for i in MESSAGE_DATA['channels']:
        # Check if a dict has been created for specified channel
        if i["channel_id"] == channel_id:
            channel_exists_flag = 1
            m_id = (channel_id * 5000) + len(i['messages'])
            new_message = {
                'message_id': m_id,
                'u_id': u_id,
                'message': message,
                'time_created': time_stamp,
                'reacts': [],
                'is_pinned': 0,
            }
            # Add new message to list of messages
            i["messages"].append(new_message)
            break


    # Case 2: no dict has been created yet
    if channel_exists_flag == 0:
        # create channel dict
        new_channel = {
            'channel_id': channel_id,
            'messages': [],
        }
        MESSAGE_DATA['channels'].append(new_channel)

        # Append message
        for i in MESSAGE_DATA['channels']:
            # Check if a dict has been created for specified channel
            if i['channel_id'] == channel_id:
                m_id = (channel_id * 5000) + len(i['messages'])
                new_message = {
                    'message_id': m_id,
                    'u_id': u_id,
                    'message': message,
                    'time_created': time_stamp,
                    'reacts': [],
                    'is_pinned': 0,
                }
                # Add new message to list of messages
                i["messages"].append(new_message)

    return {
        'message_id': m_id
    }

def message_sendlater(token, channel_id, message, time_sent, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-arguments
    '''
    Send a message at a later time specified
    '''
    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Checking that time_sent is not in the past
    if time_sent < time_stamp:
        raise InputError("Time sent is a time in the past")

    # checking message has no more than 1k chars
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Checking that the token belong to a valid user
    real_user = 0
    for i in USER_DATA['users']:
        if i['token'] == token:
            real_user = 1
            break
    assert real_user == 1

    # Checking that channel exists
    channel_exists = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            channel_exists = 1
            break

    if channel_exists == 0:
        raise InputError("Channel ID is not a valid channel")

    # Getting user's u_id
    u_id = queryUserData('token', token, USER_DATA).get('u_id')

    # Checking that user has joined the channel they are trying to post to
    joined_channel = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id:
                    joined_channel = 1
                    break

    if joined_channel == 0:
        raise AccessError("The authorised user has not joined the channel \
            they are trying to post to")

    # Set up scheduler
    S = sched.scheduler(time.time, time.sleep)
    # Schedule when you want the action to occur
    S.enterabs(time_sent, 0, send_later, \
        argument=(u_id, channel_id, message, time_sent, USER_DATA, CHANNEL_DATA, MESSAGE_DATA))
    # Block until the action has been run
    S.run()

def message_react(token, message_id, react_id): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Allows the user to react to a specific message
    '''
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
    if message['is_pinned'] == 1:
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
    Message.update_message_attribute('message_id', message_id, 'is_pinned', 1)

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
    if message['is_pinned'] == 0:
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
    Message.update_message_attribute('message_id', message_id, 'is_pinned', 0)

    return {}
