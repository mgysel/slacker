'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Testing functions in channels.py
'''
import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")

from error import AccessError, InputError   # pylint: disable=no-name-in-module, wrong-import-position
from auth import auth_register  # pylint: disable=import-error, wrong-import-position
from channels import channels_create, channels_listall, channels_list   # pylint: disable=import-error, wrong-import-position


'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
@pytest.fixture
def user_data_init():
    '''
    Sets-up USER_DATA
    '''
    return {'num_users': 0, 'users': []}


@pytest.fixture
def channel_data_init():
    '''
    Sets-up CHANNEL_DATA
    '''
    return {'num_channels': 0, 'channels': []}


'''
########## Tests for channels_list bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_channels_list(user_data_init, channel_data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard listing channels user is in, own channels
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']

    channels_create(user_one_token, 'Jades channel 1', False, CHANNEL_DATA, USER_DATA)
    channels_create(user_one_token, 'Jades channel 2', True, CHANNEL_DATA, USER_DATA)
    channels_create(user_one_token, 'Jades channel 3', False, CHANNEL_DATA, USER_DATA)

    user_one_channels = channels_list(user_one_token, CHANNEL_DATA, USER_DATA)
    assert user_one_channels['channels'] == [{
        'channel_id': 0,
        'name': 'Jades channel 1'
        }, {
            'channel_id': 1,
            'name': 'Jades channel 2'
        }, {
            'channel_id': 2,
            'name': 'Jades channel 3'
        }]


def test_channels_list_2_users(user_data_init, channel_data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard listing channels user is in, other users channels
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']

    user_two = auth_register('jade2@uni.com.au', 'Jadesuniacc33', 'Jadetwo', 'Burgertwo', USER_DATA)
    user_two_token = user_two['token']

    channels_create(user_one_token, 'Jades channel 1', False, CHANNEL_DATA, USER_DATA)

    user_one_channels = channels_list(user_two_token, CHANNEL_DATA, USER_DATA)
    assert user_one_channels['channels'] == []


def test_channels_list_invalid_token(user_data_init, channel_data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']
    channels_create(user_one_token, 'Jades channel 1', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError):
        channels_list('NOT_A_TOKEN', CHANNEL_DATA, USER_DATA)


'''
########## Tests for channels_listall bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_channels_listall_one_channel(user_data_init, channel_data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard listing all channels, own channels
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    usr = auth_register('mikegysel4321@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    channels_create(usr['token'], 'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    result = channels_listall(usr['token'], CHANNEL_DATA, USER_DATA)
    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Mikes channel'
        }]


def test_channels_listall_2_users(user_data_init, channel_data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard listing all channels other user calls
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    usr1 = auth_register('mikegysel4321@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    channels_create(usr1['token'], 'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)

    result = channels_listall(usr2['token'], CHANNEL_DATA, USER_DATA)
    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Mikes channel'
        }]


def test_channels_listall_multiple_channels(user_data_init, channel_data_init): # pylint: disable=redefined-outer-name
    '''
    Test for multiple channels
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    # Create two more channels
    usr = auth_register('mikegysel4321@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    channels_create(usr['token'], 'Mikes channel 1', False, CHANNEL_DATA, USER_DATA)
    channels_create(usr['token'], 'Mikes channel 2', True, CHANNEL_DATA, USER_DATA)

    result = channels_listall(usr['token'], CHANNEL_DATA, USER_DATA)
    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Mikes channel 1'
        }, {
            'channel_id': 1,
            'name': 'Mikes channel 2'
        }]


def test_channels_listall_invalid_token(user_data_init, channel_data_init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    usr = auth_register('mikegysel4321@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    channels_create(usr['token'], 'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError):
        channels_listall('NOT_A_TOKEN', CHANNEL_DATA, USER_DATA)


'''
########## Tests for channels_create bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_channels_create(user_data_init, channel_data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard creating a private channel
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']

    new_ch_id = channels_create(user_one_token, 'Jades new channel', False, CHANNEL_DATA, USER_DATA)

    assert new_ch_id['channel_id'] >= 0 and new_ch_id['channel_id'] is not None


def test_channels_create_public(user_data_init, channel_data_init): # pylint: disable=redefined-outer-name
    '''
    Test for standard creating a public channel
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']

    new_ch_id = channels_create(user_one_token, 'Jades new channel', True, CHANNEL_DATA, USER_DATA)

    assert new_ch_id['channel_id'] >= 0 and new_ch_id['channel_id'] is not None


def test_channels_create_long_name(user_data_init, channel_data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for name longer than 20 characters
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    user_one = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    user_one_token = user_one['token']

    with pytest.raises(InputError):
        channels_create(user_one_token, 'j'*23, False, CHANNEL_DATA, USER_DATA)


def test_channels_create_invalid_token(user_data_init, channel_data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = user_data_init  # pylint: disable=invalid-name
    CHANNEL_DATA = channel_data_init    # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        channels_create('NOT_A_TOKEN', 'Jades new channel', False, CHANNEL_DATA, USER_DATA)
