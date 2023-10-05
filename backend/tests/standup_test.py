'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  08/03/2020
Description:    Testing functions in other.py
'''

import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")
from error import AccessError, InputError
from datetime import datetime, timedelta, time
from auth import auth_register
from channels import channels_create
from channel import get_channel_data
from other import standup_active, standup_send, standup_start



'''
########## Helper functions ##########
'''
@pytest.fixture
def user_data_init():
    '''
    Init user data
    '''
    return {'num_users': 0, 'users': []}

@pytest.fixture
def channel_data_init():
    '''
    Init channel data
    '''
    return {'num_channels': 0, 'channels': []}

@pytest.fixture
def message_data_init():
    '''
    Init message data
    '''
    return {'channels': []}

@pytest.fixture
def user_one_init(user_data_init):
    '''
    Create user one
    '''
    USER_DATA = user_data_init
    email = 'jade@uni.com.au'
    password = 'Jadesuniacc33'
    name_first = 'Jade'
    name_last = 'Burger'
    return auth_register(email, password, name_first, name_last, USER_DATA)

@pytest.fixture
def user_two_init(user_data_init):
    '''
    Create user_two
    '''
    USER_DATA = user_data_init
    email = 'mike@uni.com.au'
    password = 'Mike!123'
    name_first = 'Mike'
    name_last = 'Gysel'
    return auth_register(email, password, name_first, name_last, USER_DATA)

@pytest.fixture
def channel_one_init(user_one_init, user_data_init, channel_data_init):
    '''
    Create channel_one
    '''
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    user = user_one_init

    name = 'Jades channel'
    is_public = False

    return channels_create(user['token'], name, is_public, \
        CHANNEL_DATA, USER_DATA)

@pytest.fixture
def channel_two_init(user_two_init, user_data_init, channel_data_init):
    '''
    Create channel_two
    '''
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    user = user_two_init

    name = 'Mikes channel'
    is_public = True

    return channels_create(user['token'], name, is_public, \
        CHANNEL_DATA, USER_DATA)


'''
########## Tests for standup_start below ##########
'''

def test_standup_start_success(user_data_init, channel_data_init, \
    message_data_init, user_one_init, channel_one_init):
    '''
    Successful attempt at starting standup
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 3
    return_data = standup_start(user['token'], channel['channel_id'], \
        length, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check MESSAGE_DATA updated
    standup_data = get_channel_data(channel['channel_id'], CHANNEL_DATA)['standup']
    assert standup_data['is_active'] == 1
    assert standup_data['time_finish'] < datetime.now() + \
        timedelta(seconds=length)
    assert standup_data['message'] is None

    # Check return results
    assert return_data < datetime.now() + timedelta(seconds=length)

    # Check MESSAGE_DATA reupdated after length of time finishes
    time.sleep(length + 1)
    s_data = get_channel_data(channel['channel_id'], \
        CHANNEL_DATA)
    standup_data= s_data['standup']
    assert standup_data['is_active'] == 0
    assert standup_data['time_finish'] is None
    assert standup_data['message'] is None


def test_standup_start_input_error_invalid_channel_id(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to invalid channel id
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    invalid_channel_id = channel['channel_id'] + 1
    length = 1

    # Check if InputError Raised
    with pytest.raises(InputError) as e:
        standup_start(user['token'], invalid_channel_id, length, \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)


def test_standup_start_input_error_standup_in_progress(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to current standup in progress
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 1

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check if InputError Raised
    with pytest.raises(InputError) as e:
        standup_start(user['token'], channel['channel_id'], length, \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

'''
########## Tests for standup_active below ##########
'''

def test_standup_active(user_data_init, channel_data_init, message_data_init, \
    user_one_init, channel_one_init):
    '''
    Successful attempt at returning active standup
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 10

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check return data
    return_data = standup_active(user['token'], channel['channel_id'], \
        USER_DATA, CHANNEL_DATA)
    assert return_data['is_active'] == 1
    assert datetime.strptime(return_data['time_finish'], \
        '%Y %m %d %H %M %S') < datetime.now() + timedelta(seconds=length)

    # Check CHANNEL_DATA updated
    standup_data = get_channel_data(channel['channel_id'], \
        CHANNEL_DATA)['standup']
    assert standup_data['is_active'] == 1
    assert standup_data['time_finish'] < datetime.now() + \
        timedelta(seconds=length)
    assert standup_data['message'] is None


def test_standup_inactive(user_data_init, channel_data_init, \
    user_one_init, channel_one_init):
    '''
    Successful attempt at returning inactive standup
    '''
    # Init data
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    user = user_one_init
    channel = channel_one_init

    # Check return data
    return_data = standup_active(user['token'], channel['channel_id'], USER_DATA, CHANNEL_DATA)
    assert return_data['is_active'] == 0
    assert return_data['time_finish'] is None

    # Check CHANNEL_DATA updated
    standup_data = get_channel_data(channel['channel_id'], CHANNEL_DATA)['standup']
    assert standup_data['is_active'] == 0
    assert standup_data['time_finish'] is None
    assert standup_data['message'] is None


def test_standup_active_input_error(user_data_init, channel_data_init, \
    user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at returning inactive standup
    Input Error due to invalid channel id
    '''
    # Init data
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    user = user_one_init
    channel = channel_one_init
    invalid_channel_id = channel['channel_id'] + 1

    # Check error
    with pytest.raises(InputError) as e:
        standup_active(user['token'], invalid_channel_id, \
        USER_DATA, CHANNEL_DATA)


'''
########## Tests for standup_start below ##########
'''

def test_standup_start_success(user_data_init, channel_data_init, \
    message_data_init, user_one_init, channel_one_init):
    '''
    Successful attempt at starting standup
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 1
    return_data = standup_start(user['token'], channel['channel_id'], \
        length, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check MESSAGE_DATA updated
    standup_data = get_channel_data(channel['channel_id'], CHANNEL_DATA)['standup']
    assert standup_data['is_active'] == 1
    assert standup_data['time_finish'] < datetime.now() + \
        timedelta(seconds=length)
    assert standup_data['message'] is None

    # Check return results
    time_finish = datetime.strptime(return_data['time_finish'], \
        '%Y %m %d %H %M %S')
    assert time_finish < datetime.now() + timedelta(seconds=length)


def test_standup_start_input_error_invalid_channel_id(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to invalid channel id
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    invalid_channel_id = channel['channel_id'] + 1
    length = 1

    # Check if InputError Raised
    with pytest.raises(InputError) as e:
        standup_start(user['token'], invalid_channel_id, length, \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)


def test_standup_start_input_error_standup_in_progress(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to current standup in progress
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 1

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check if InputError Raised
    with pytest.raises(InputError) as e:
        standup_start(user['token'], channel['channel_id'], length, \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)


'''
########## Tests for standup_send below ##########
'''

def test_standup_send_success(user_data_init, channel_data_init, \
    message_data_init, user_one_init, channel_one_init):
    '''
    Successful attempt at standup_send
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 1
    message = 'Hello'

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    return_data = standup_send(user['token'], channel['channel_id'], message, \
        USER_DATA, CHANNEL_DATA)

    # Check CHANNEL_DATA updated
    standup_data = get_channel_data(channel['channel_id'], CHANNEL_DATA)['standup']
    assert standup_data['is_active'] == 1
    assert standup_data['time_finish'] < datetime.now() + \
        timedelta(seconds=length)
    assert standup_data['message'] == f"Jade {message} \n"

    # Check return results
    assert (return_data == {})


def test_standup_send_input_error_invalid_channel_id(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid channel id
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    invalid_channel_id = channel['channel_id'] + 1
    length = 1
    message = 'Hello'

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check error
    with pytest.raises(InputError) as e:
        standup_send(user['token'], invalid_channel_id, message, \
            USER_DATA, CHANNEL_DATA)


def test_standup_send_input_error_invalid_message(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid message
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    length = 1
    message = 'Hello' * 1000

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check error
    with pytest.raises(InputError) as e:
        standup_send(user['token'], channel['channel_id'], message, \
            USER_DATA, CHANNEL_DATA)


def test_standup_send_input_error_standup_not_progress(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to active standup not currently in progress
    '''
    # Init data
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    channel = channel_one_init
    message = 'Hello'

    # Check error
    with pytest.raises(InputError) as e:
        standup_send(user['token'], channel['channel_id'], message, \
            USER_DATA, CHANNEL_DATA)


def test_standup_send_input_error_unauthorised_user(user_data_init, \
    channel_data_init, message_data_init, user_one_init, channel_one_init, \
    user_two_init):
    '''
    Unsuccessful attempt at standup_send
    Access Error due to authorised user not a part of the channel
    '''
    # Start Standup
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    user = user_one_init
    user_two = user_two_init
    channel = channel_one_init
    length = 1
    message = 'Hello'

    standup_start(user['token'], channel['channel_id'], length, \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

    # Check error
    with pytest.raises(AccessError) as e:
        standup_send(user_two['token'], channel['channel_id'], message, \
            USER_DATA, CHANNEL_DATA)
