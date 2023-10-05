'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  28/03/2020
Description:    Testing functions in other.py with Flask wrapping
'''

import urllib
import json
import sys
from datetime import datetime, timedelta
import pytest


# If run from src folder allows importing of files
sys.path.append(".")
# If run in src/tests allows importing of files
sys.path.append("..")
# If run just outside src allows importing of files
sys.path.append("./src")


'''
########## Helper function and variable used throughout tests ##########
'''
BASE_URL = 'http://127.0.0.1:8080'

@pytest.fixture
def init():
    '''
    Function to reset server state and pass user info
    to the test functions
    '''
    # Reseting work space
    urllib.request.urlopen(f"{BASE_URL}/workspace/reset", data={})

    # Create users
    usr1_data = json.dumps({
                'email': 'person@gmail.com',
                'password': 'V3ryG00d@m3',
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
                }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", \
        data=usr1_data, headers={'Content-Type': 'application/json'})
    usr1 = json.load(urllib.request.urlopen(req))

    usr2_data = json.dumps({
                'email': 'NotPerson@email.com',
                'password': 'V3ryd!ff3r3nt@m3',
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
                }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", \
        data=usr2_data, headers={'Content-Type': 'application/json'})
    usr2 = json.load(urllib.request.urlopen(req))

    # Create channel 1
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
        'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
        headers={'Content-Type': 'application/json'}, method='POST')
    chnl1 = json.load(urllib.request.urlopen(req))

    # Create channel 2
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
        'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
        headers={'Content-Type': 'application/json'}, method='POST')
    chnl2 = json.load(urllib.request.urlopen(req))

    return {'usr1': usr1, 'usr2': usr2, 'chnl1': chnl1, 'chnl2': chnl2}

'''
########## Tests for standup_active below ##########
'''

def test_standup_inactive(init):
    '''
    Successful attempt at returning inactive standup
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']

    # Calling standup_active
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chnl1['channel_id'],
    })
    req = f'{BASE_URL}/standup/active?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['is_active'] == 0
    assert result['time_finish'] is None


def test_standup_active_input_error(init):
    '''
    Unsuccessful attempt at returning inactive standup
    Input Error due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl2 = init['chnl2']
    invalid_channel_id = chnl2['channel_id'] + 1

    # Calling standup_active
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': invalid_channel_id,
    })
    req = f'{BASE_URL}/standup/active?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

'''
########## Tests for standup_start below ##########
'''

def test_standup_start_success(init):
    '''
    Test for standard listing channels user is in, own channels
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']
    length = 1

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    assert datetime.strptime(result['time_finish'], '%Y %m %d %H %M %S') < \
        datetime.now() + timedelta(seconds=length)

def test_standup_start_input_error_invalid_channel_id(init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl2 = init['chnl2']
    invalid_channel_id = chnl2['channel_id'] + 1
    length = 1

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': invalid_channel_id, 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check if InputError Raised
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_standup_start_input_error_standup_in_progress(init):
    '''
    Unsuccessful attempt at starting standup
    InputError raised due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl2 = init['chnl2']
    invalid_channel_id = chnl2['channel_id'] + 1
    length = 1

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': invalid_channel_id, 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Calling standup_start again
    data = json.dumps({'token': usr1['token'], \
        'channel_id': invalid_channel_id, 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check if InputError Raised when starting another standup
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for standup_send below ##########
'''

def test_standup_send_success(init):
    '''
    Test for standard listing channels user is in, own channels
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']
    length = 10

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    # Call standup_send
    message = 'Hello'
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    assert result == {}


def test_standup_send_input_error_invalid_channel_id(init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']
    length = 10

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Call standup_send
    message = 'Hello'
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'] + 100, \
        'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check error
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_standup_send_input_error_invalid_message(init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']
    length = 10

    # Calling standup_start
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'length': length}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/start", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Call standup_send
    message = 'Hello' * 1000
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check error
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_standup_send_input_error_standup_not_progress(init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid channel id
    '''
    usr1 = init['usr1']
    chnl1 = init['chnl1']

    # Call standup_send
    message = 'Hello'
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chnl1['channel_id'], 'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check error
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_standup_send_access_error_unauthorised_user(init):
    '''
    Unsuccessful attempt at standup_send
    Input Error due to invalid channel id
    '''
    usr2 = init['usr2']
    chnl1 = init['chnl1']

    # Call standup_send
    message = 'Hello'
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chnl1['channel_id'], 'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/standup/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    # Check error
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
