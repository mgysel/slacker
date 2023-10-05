'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  08/03/2020
Description:    Testing functions in other.py
'''

import sys
sys.path.append("..")

import pytest
from error import AccessError, InputError
from other import search, users_all
from auth import auth_register, auth_login
from channels import channels_create
from message import message_send, message_remove, message_edit

@pytest.fixture
def user_data_init():
    return {'num_users': 0, 'users': []}


@pytest.fixture
def channel_data_init():
    return {'num_channels': 0, 'channels': []}

@pytest.fixture
def message_data_init():
    return {'channels': []}
 
'''
########## Tests for search below ##########
'''
# Base case - search function works 
def test_search_working(user_data_init, channel_data_init, message_data_init): 
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    valid_credentials = auth_register('test_email@google.com', \
    'a_random_test_password123','Atest', 'User', USER_DATA)
    valid_channel = channels_create(valid_credentials["token"], \
    'test_channel', False, CHANNEL_DATA, USER_DATA)
    message_id  = message_send(valid_credentials['token'], \
    valid_channel['channel_id'], 'find me', USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    valid_query_string = 'find me'
    search_dict = search(valid_credentials['token'], valid_query_string, \
    USER_DATA, MESSAGE_DATA)
    assert search_dict['message'][0] != None

# Base case - search returns no matches 
def test_search_no_matches(user_data_init, channel_data_init, message_data_init): 
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init
    valid_credentials = auth_register('test_email@google.com', \
    'a_random_test_password123','Atest', 'User', USER_DATA)
    valid_channel = channels_create(valid_credentials['token'], \
    'test_channel', False, CHANNEL_DATA, USER_DATA)
    message_id  = message_send(valid_credentials['token'], \
    valid_channel['channel_id'], 'find me', USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
    valid_query_string = "yyyyyyyyyyyyyyyyy"
    search_dict = search(valid_credentials['token'], valid_query_string, \
    USER_DATA, MESSAGE_DATA)
    assert len(search_dict['message']) == 0


'''
########## Tests for users_all below ##########
'''
# Test users_all when there is one user
def test_users_all_one(user_data_init):
    # Create authorized user, retrieve u_id and token
    USER_DATA = user_data_init
    first_name = 'Mike'
    last_name = 'Gysel'
    email = 'mikegysel4321@gmail.com'
    token_uid = \
    auth_register(email, 'ThisisPW1234!', first_name, last_name, \
    USER_DATA)
    u_id = token_uid['u_id']
    token = token_uid['token']
    assert users_all(token, USER_DATA) == \
    {
        'user': [
            {
                'u_id': u_id,
                'email': email,
                'name_first': first_name,
                'name_last': last_name,
            },
        ],
    }

# Test users_all when there are multiple user
def test_users_all_multiple(user_data_init):
    # Create two authorized user, retrieve u_id and token
    USER_DATA = user_data_init
    first_name_one = 'Mike'
    last_name_one = 'Gysel'
    email_one = 'mikegysel4321@gmail.com'
    token_uid = \
    auth_register(email_one, 'ThisisPW1234!', first_name_one, last_name_one, \
    USER_DATA)
    u_one_id = token_uid['u_id']
    token_one = token_uid['token']
    
    first_name_two =  'NotMike'
    last_name_two =  'NotGysel'
    email_two = 'mikegysel432@gmail.com'
    token_uid = \
    auth_register(email_two, 'ThisisPW1234!', first_name_two, last_name_two, \
    USER_DATA)
    u_two_id = token_uid['u_id']
    token_two = token_uid['token']
    
    assert users_all(token_one, USER_DATA) == \
    {
        'user': [
            {
                'u_id': u_one_id,
                'email': email_one,
                'name_first': first_name_one,
                'name_last': last_name_one,
            },
            {
                'u_id': u_two_id,
                'email': email_two,
                'name_first': first_name_two,
                'name_last': last_name_two,
            }
        ]
    }    

 # Test users_all when there is an invalid token passed   
def test_users_all_invalid_token(user_data_init):
    # HELPER VARIABLES
    # Create authorized user, retrieve u_id and token
    USER_DATA = user_data_init
    first_name = 'Mike'
    last_name = 'Gysel'
    email = 'mikegysel4321@gmail.com'
    token_uid = \
    auth_register(email, 'ThisisPW1234!', first_name, last_name, USER_DATA)
    u_id = token_uid.get('u_id')
    token = token_uid.get('token')
    
    with pytest.raises(AccessError) as e:
        users_all('NOTATOKEN', USER_DATA)
