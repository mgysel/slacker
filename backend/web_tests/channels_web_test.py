'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  26/03/2020
Description:    Testing functions in channels.py with Flask wrapping
'''
import urllib.request
import json
import pytest


'''
########## Helper function and variable used throughout tests ##########
'''                                             # pylint: disable=pointless-string-statement
BASE_URL = 'http://127.0.0.1:8080'

@pytest.fixture
def init():
    '''
    Function to reset server state and pass user info
    to the test functions
    '''
    # Reseting work space
    urllib.request.urlopen(f"{BASE_URL}/workspace/reset", data={})

    # Making users
    usr1_data = json.dumps({
                'email': 'person@gmail.com',
                'password': 'V3ryG00d@m3',
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
                }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=usr1_data, \
                                headers={'Content-Type': 'application/json'})
    usr1 = json.load(urllib.request.urlopen(req))

    usr2_data = json.dumps({
                'email': 'NotPerson@email.com',
                'password': 'V3ryd!ff3r3nt@m3',
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
                }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=usr2_data, \
                                headers={'Content-Type': 'application/json'})
    usr2 = json.load(urllib.request.urlopen(req))

    return {'usr1': usr1, 'usr2': usr2}


'''
########## Tests for channels_list bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channels_list(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard listing channels user is in, own channels
    '''
    usr1 = init['usr1']

    # Creating channel that is private
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                    'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_list
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
    })
    req = f'{BASE_URL}/channels/list?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }]

    # Creating second channel that is public
    data = json.dumps({'token': usr1['token'], 'name': 'Channel 2 Idriz', \
                                    'is_public': True}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_list
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
    })
    req = f'{BASE_URL}/channels/list?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }, {
            'channel_id': 1,
            'name': 'Channel 2 Idriz'
        }]


def test_web_channels_list_2_users(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard listing channels user is in, other users channels
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Creating channel that is private
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_list
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
    })
    req = f'{BASE_URL}/channels/list?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == []


def test_web_channels_list_invalid_token(init):     # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    usr1 = init['usr1']

    # Creating channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_list with invalid token
    query_string = urllib.parse.urlencode({
        'token': 'NOT_A_TOKEN',
    })
    req = f'{BASE_URL}/channels/list?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channels_listall bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channels_listall(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard listing all channels, own channels
    '''
    usr1 = init['usr1']

    # Creating channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_listall
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
    })
    req = f'{BASE_URL}/channels/listall?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }]

    # Creating second channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel 2 Idriz', \
                                    'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_listall
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
    })
    req = f'{BASE_URL}/channels/listall?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }, {
            'channel_id': 1,
            'name': 'Channel 2 Idriz'
        }]


def test_web_channels_listall_2_users(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard listing all channels other user calls
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Creating channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 calling channels_listall
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
    })
    req = f'{BASE_URL}/channels/listall?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }]

    # usr2 creating channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel NotIdriz', \
                                    'is_public': True}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 calling channels_listall
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
    })
    req = f'{BASE_URL}/channels/listall?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz'
        }, {
            'channel_id': 1,
            'name': 'Channel NotIdriz'
        }]


def test_web_channels_listall_invalid_token(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    usr1 = init['usr1']

    # Creating channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                    'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Calling channels_listall with invalid token
    query_string = urllib.parse.urlencode({
        'token': 'NOT_A_TOKEN',
    })
    req = f'{BASE_URL}/channels/listall?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channels_create bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channels_create(init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard creating a private channel
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                    'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    assert result['channel_id'] >= 0 and result['channel_id'] is not None


def test_web_channels_create_public(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard creating a public channel
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                    'is_public': True}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    assert result['channel_id'] >= 0 and result['channel_id'] is not None


def test_web_channels_create_long_name(init):   # pylint: disable=redefined-outer-name
    '''
    Test for name longer than 20 characters
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name': 'I'*21, \
                        'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channels_create_invalid_token():   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    data = json.dumps({'token': 'NOT_A_TOKEN', 'name': 'I'*21, \
                        'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
