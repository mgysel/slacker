'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  25/03/2020
Description:    Testing functions in auth.py
'''
#pylint: disable=no-name-in-module,wrong-import-position,wrong-import-order,import-error
#pylint: disable=missing-function-docstring
import time
import pytest
import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")
from error import AccessError, InputError
from auth import auth_register
from channels import channels_create
from channel import channel_join
from message import message_send, message_remove, message_edit, \
    message_sendlater, message_react, message_unreact, message_pin, message_unpin

'''
########## Helper functions ##########
'''
@pytest.fixture
def user_data_init():
    return {'num_users': 0, 'users': []}


@pytest.fixture
def channel_data_init():
    return {'num_channels': 0, 'channels': []}

@pytest.fixture
def message_data_init():
    return {'channels': []}

########## testing... message_send ##########

# Base case - message_send function works
def test_message_send_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Input Error - when message is more than 1k char
def test_message_send_input_error(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    more_than_1k_chars = "x" * 1001
    with pytest.raises(InputError):
        message_send(valid_credentials["token"], \
            valid_channel["channel_id"], more_than_1k_chars, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Input Error - when the user tries to send a message to a channel which doesn't exist
def test_message_send_fail(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    an_invalid_channel_id = 9999999999
    with pytest.raises(InputError):
        message_send(valid_credentials["token"], an_invalid_channel_id, \
            "helloworld123", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Access Error - when the authorised user has not joined the channel \
# they are trying to post to
def test_message_send_access_error(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    user2 = auth_register("test2_email@google.com", "a_random_test2_password123", \
        "Atesttwo", "Usertwo", USER_DATA)
    with pytest.raises(AccessError):
        message_send(user2["token"], valid_channel["channel_id"], \
            "helloworld123", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)


########## testing... message_remove ##########

# Base case - message_remove function works
def test_message_remove_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], valid_channel["channel_id"], \
        "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    test = message_remove(valid_credentials["token"], message_id["message_id"], \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    assert test == {}

# Test for Input Error - trying to remove a message (based on ID) that no longer exists
def test_message_remove_input_error(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_remove(valid_credentials["token"], message_id["message_id"], \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    with pytest.raises(InputError):
        message_remove(valid_credentials["token"], message_id["message_id"], \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Access Error - Message was not sent by the authorised user making this request
def test_message_remove_access_error_1(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    user2 = auth_register("test2_email@google.com", "a_random_test2_password123", \
        "Atesttwo", "Usertwo", USER_DATA)
    channel_join(user2["token"], \
        valid_channel["channel_id"], CHANNEL_DATA, USER_DATA)
    with pytest.raises(AccessError):
        message_remove(user2["token"], message_id["message_id"],\
             USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Access Error - Authorised user is not an admin or owner of this channel/ slackr
def test_message_remove_access_error_2(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    user2 = auth_register("test2_email@google.com", \
        "a_random_test2_password123", "Atesttwo", "Usertwo", USER_DATA)
    with pytest.raises(AccessError):
        message_remove(user2["token"], message_id["message_id"], \
            USER_DATA, CHANNEL_DATA, MESSAGE_DATA)


########## testing... message_edit ##########

# Base case - message_edit function works
def test_message_edit_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    assert message_edit(valid_credentials["token"], message_id["message_id"], \
        "a_simple_test_message_edited", USER_DATA, CHANNEL_DATA, MESSAGE_DATA) == {}

# Base case - message_edit function calls message_remove if new message is an empty string
def test_message_edit_empty(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    assert message_edit(valid_credentials["token"], message_id["message_id"], "", \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA) == {}

# Test for Access Error - Message was not sent by the authorised user making this request
def test_message_edit_access_error_1(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    user2 = auth_register("test2_email@google.com", "a_random_test2_password123", \
        "Atesttwo", "Usertwo", USER_DATA)
    channel_join(user2["token"], valid_channel["channel_id"], \
        CHANNEL_DATA, USER_DATA)
    with pytest.raises(AccessError):
        message_edit(user2["token"], message_id["message_id"], \
            "a_simple_test_message_edited", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

# Test for Access Error - Authorised user is not an admin or owner of this channel/ slackr
def test_message_edit_access_error_2(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], valid_channel["channel_id"], \
        "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    user2 = auth_register("test2_email@google.com", \
        "a_random_test2_password123", "Atesttwo", "Usertwo", USER_DATA)
    with pytest.raises(AccessError):
        message_edit(user2["token"], message_id["message_id"], \
            "a_simple_test_message_edited", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_sendlater_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    message_sendlater(valid_credentials["token"], valid_channel["channel_id"], \
        "a_simple_test_message", int(time.time() + 10), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_sendlater_invalid_channelid(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)
    an_invalid_channel_id = 9999999999
    with pytest.raises(InputError):
        message_sendlater(valid_credentials["token"], an_invalid_channel_id, \
            "helloworld123", int(time.time() + 10), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_sendlater_1kchars(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 1, CHANNEL_DATA, USER_DATA)
    more_than_1k_chars = "x" * 1001
    with pytest.raises(InputError):
        message_sendlater(valid_credentials["token"], valid_channel["channel_id"], \
            more_than_1k_chars, int(time.time() + 10), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_sendlater_timesent(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    with pytest.raises(InputError):
        message_sendlater(valid_credentials["token"], valid_channel["channel_id"], \
            "a_simple_test_message", int(time.time() - 1000), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_sendlater_unjoinedchannel(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], "test_channel", 0, \
        CHANNEL_DATA, USER_DATA)
    user2 = auth_register("test2_email@google.com", "a_random_test2_password123", \
        "Atesttwo", "Usertwo", USER_DATA)
    with pytest.raises(AccessError):
        message_sendlater(user2["token"], valid_channel["channel_id"], \
            "helloworld123", int(time.time() + 10), USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_messagereact_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], "test_channel", 0, \
        CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_react(valid_credentials["token"], \
        message_id["message_id"], 1, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_message_unreact_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
        "test_channel", 0, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], \
        valid_channel["channel_id"], "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_react(valid_credentials["token"], message_id["message_id"], \
        1, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_unreact(valid_credentials["token"], \
        message_id["message_id"], 1, USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_message_pin_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], "test_channel", \
        0, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], valid_channel["channel_id"], \
        "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_pin(valid_credentials["token"], message_id["message_id"], \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)

def test_message_unpin_working(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    valid_credentials = auth_register("test_email@google.com", "a_random_test_password123", \
        "Atest", "User", USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], "test_channel", \
        0, CHANNEL_DATA, USER_DATA)
    message_id = message_send(valid_credentials["token"], valid_channel["channel_id"], \
        "a_simple_test_message", USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_pin(valid_credentials["token"], message_id["message_id"], \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    message_unpin(valid_credentials["token"], message_id["message_id"], \
        USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
