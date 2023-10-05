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
                    message_send(token, channel_id, "++++++++++ START OF ROUND ++++++++++", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    message = HANGMAN[0]
                    message_send(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    message_send(token, channel_id, "Word is {}".format(x['guessed_word']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    message_send(token, channel_id, "You have used 0/7 Guesses", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    message_send(token, channel_id, "To guess enter: '/guess X'", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                else: 
                    message_send(token, channel_id, "Game in progress. To guess enter: '/guess X'", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
        
    if message.startswith("/guess") is True:
        
        channelexists_flag = 0
        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                channelexists_flag = 1
                break

        # If the game has not yet started
        if channelexists_flag == 0:
            message_send(token, channel_id, "You have not yet started a game. To start enter: '/hangman'", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
        else:
            guess = message.split(" ")
            if len(guess) < 2:
                message_send(token, channel_id, "Invalid entry: to guess enter '/guess X'", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                return
            guess = guess[1]

        for x in HANGMAN_DATA['channels']:
            if x['channel_id'] == channel_id:
                message_send(token, channel_id, "++++++++++ START OF ROUND ++++++++++", USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
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
                message_send(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                message_send(token, channel_id, "WORD IS: {} \n".format(x['guessed_word']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                message_send(token, channel_id, "YOU HAVE USED {}/7 LIVES: {}".format(WRONG, "X " * WRONG), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                message_send(token, channel_id, "YOU HAVE GUESSED THESE LETTERS/ WORDS: {}".format(x['guesses']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)

                # check if the team has won
                if x['guessed_word'] == x['word']:
                    message_send(token, channel_id, "++++++++++ CONGRATULATIONS YOU WIN!!! THE WORD WAS {} ++++++++++".format(x['word']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    x['word'] = ""
                    x['guessed_word'] = ""
                    x['wrong'] = 0
                    x['guesses'] = []
                    x['in_progress'] = 0

                # check if the team has lost
                if x['wrong'] == 7:
                    message_send(token, channel_id, "{}".format(HANGMAN[7]), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    message_send(token, channel_id, "YOU WERE HANGED. GAME OVER. THE WORD WAS {}".format(x['word']), USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)
                    x['word'] = ""
                    x['guessed_word'] = ""
                    x['wrong'] = 0
                    x['guesses'] = []
                    x['in_progress'] = 0       
            break


def message_send(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA): # pylint: disable=invalid-name,too-many-arguments,too-many-locals,too-many-branches
    '''
    Sends a message to a valid channel
    '''
    # checking message has no more than 1k chars
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # Checking that the channel_id is valid
    real_channel = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            real_channel = 1
            break

    if not real_channel:
        raise InputError("Channel ID is invalid")

    # Checking that the token belong to a valid user
    real_user = 0
    for i in USER_DATA['users']:
        if i['token'] == token:
            real_user = 1
            break

    if not real_user:
        raise AccessError("Invalid token")

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

    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Call hangman function 
    if message == "/hangman" or message.startswith("/guess") is True:
        hangman(token, channel_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA, HANGMAN_DATA)

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

def message_remove(token, message_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-branches
    '''
    Removes a message that has already been sent
    '''
    # Checking that the token belong to a valid user
    real_user = 0
    for i in USER_DATA['users']:
        if i['token'] == token:
            real_user = 1
            break

    assert real_user == 1

    # Getting user's u_id
    u_id = queryUserData('token', token, USER_DATA).get('u_id')

    # Checking that message exists
    message_exists = 0
    channel_id = 0
    sent_by = 0

    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                if j['u_id'] == u_id:
                    sent_by = 1
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    is_owner = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id and j['rank'] == 1:
                    is_owner = 1
                    break

    if sent_by == 1 or is_owner == 1:
        for i in MESSAGE_DATA['channels']:
            for j in i['messages']:
                if j['message_id'] == message_id:
                    i['messages'].remove(j)
                    break
    else:
        raise AccessError("Cannot remove: User did not send the message \
            and user is not an owner of the channel")

    return {}


def message_edit(token, message_id, message, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Edits a message that has already been sent
    '''
    # checking message has no more than 1k chars
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    # If the new message is an empty string remove the message
    if message == '':
        message_remove(token, message_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
        return {}

    # Checking that the token belong to a valid user
    real_user = 0
    for i in USER_DATA['users']:
        if i['token'] == token:
            real_user = 1
            break

    assert real_user == 1

    # Getting user's u_id
    u_id = queryUserData('token', token, USER_DATA).get('u_id')

    # Getting time_stamp of message
    time_stamp = int(time.time())

    # Checking that message exists
    message_exists = 0
    channel_id = 0
    sent_by = 0

    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                if j['u_id'] == u_id:
                    sent_by = 1
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    is_owner = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id and j['rank'] == 1:
                    is_owner = 1
                    break


    if sent_by == 1 or is_owner == 1:
        for i in MESSAGE_DATA['channels']:
            for j in i['messages']:
                if j['message_id'] == message_id:
                    j['message'] = message
                    j['u_id'] = u_id
                    j['time_created'] = time_stamp
                    break
    else:
        raise AccessError("Cannot remove: User did not send the message \
            and user is not an owner of the channel")

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


def message_react(token, message_id, react_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Allows the user to react to a specific message
    '''
    if react_id != 1:
        raise InputError("Not a valid react_id. The only valid react ID the frontend has is 1")

    # Checking that message exists
    message_exists = 0
    channel_id = 0
    already_reacted = 0
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                already_reacted = j['reacts']
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    u_id = queryUserData('token', token, USER_DATA).get('u_id')

    is_member = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id:
                    is_member = 1
                    break

    if (message_exists == 0 or is_member == 0):
        raise InputError("Message id is not a valid message within a channel \
            that the authorised user has joined")

    if react_id == already_reacted:
        raise InputError("Message already contains an active React with ID react_id")

    # Adding the react
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                j['reacts'] = react_id
                break

    return {}

def message_unreact(token, message_id, react_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-arguments,too-many-branches
    '''
    Allows a user to unreact to a message
    '''
    if react_id != 1:
        raise InputError("Not a valid react_id. The only valid react ID the frontend has is 1")

   # Checking that message exists
    message_exists = 0
    channel_id = 0
    has_react = 0
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                if j['reacts'] == react_id:
                    has_react = 1
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    if has_react == 0:
        raise InputError("Message does not contain an active React with ID react_id")

    u_id = queryUserData('token', token, USER_DATA).get('u_id')
    is_member = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id:
                    is_member = 1
                    break

    if (message_exists == 0 or is_member == 0):
        raise InputError("Message id is not a valid message within a channel \
            that the authorised user has joined")

    # Unreacting to message
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                j['reacts'] = 0
                break

    return {}

def message_pin(token, message_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-branches
    '''
    Pins a particular message for visibility
    '''
    # Checking that message exists
    message_exists = 0
    channel_id = 0
    pinned = 0
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                pinned = j['is_pinned']
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    if pinned == 1:
        raise InputError("Message is already pinned")

    u_id = queryUserData('token', token, USER_DATA).get('u_id')
    is_member = 0
    is_owner = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id:
                    is_member = 1

                if j['u_id'] == u_id and j['rank'] == 1:
                    is_owner = 1
                    break

    if is_member != 1:
        raise InputError("User is not a member of the channel that the message is within")

    if is_owner != 1:
        raise AccessError("The authorised user is not an owner")

    #pinning the message
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                j['is_pinned'] = 1
                break

    return {}

def message_unpin(token, message_id, USER_DATA, CHANNEL_DATA, MESSAGE_DATA): # pylint: disable=invalid-name,too-many-branches
    '''
    Unpins a particular message
    '''
    # Checking that message exists
    message_exists = 0
    channel_id = 0
    pinned = 0
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                message_exists = 1
                channel_id = i['channel_id']
                pinned = j['is_pinned']
                break

    if message_exists == 0:
        raise InputError("Message(based on ID) no longer exists")

    if pinned == 0:
        raise InputError("Message is already unpinned")

    u_id = queryUserData('token', token, USER_DATA).get('u_id')
    is_member = 0
    is_owner = 0
    for i in CHANNEL_DATA['channels']:
        if i['channel_id'] == channel_id:
            for j in i['members']:
                if j['u_id'] == u_id:
                    is_member = 1

                if j['u_id'] == u_id and j['rank'] == 1:
                    is_owner = 1
                    break

    if is_member != 1:
        raise InputError("User is not a member of the channel that the message is within")

    if is_owner != 1:
        raise AccessError("The authorised user is not an owner")

    #Unpinning the message
    for i in MESSAGE_DATA['channels']:
        for j in i['messages']:
            if j['message_id'] == message_id:
                j['is_pinned'] = 0
                break

    return {}
