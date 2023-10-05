# pylint: disable=too-many-lines
'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  27/03/2020
Description:    Testing functions in channel.py with Flask wrapping
'''
import urllib.request
import json
import time
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

    # Making channels
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
                                'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    chn1 = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz2', \
                                    'is_public': True}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    chn2 = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr2['token'], 'name': 'Channel NotIdriz', \
                                    'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    chn3 = json.load(urllib.request.urlopen(req))

    return {'usr1': usr1, 'usr2': usr2, 'chn1': chn1, 'chn2': chn2, 'chn3': chn3}


'''
########## Tests for channel_invite bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_invite(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard channel invite
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels usr2 is in
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
    })
    req = f'{BASE_URL}/channels/list?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz',
        }, {
            'channel_id': 2,
            'name': 'Channel NotIdriz',
        }]


def test_web_channel_invite_twice(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard channel invite, inviting user twice
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2 twice
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)
    urllib.request.urlopen(req)

    # Collecting channels usr2 is in
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
    })
    req = f'{BASE_URL}/channels/list?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['channels'] == [{
        'channel_id': 0,
        'name': 'Channel Idriz',
        }, {
            'channel_id': 2,
            'name': 'Channel NotIdriz',
        }]


def test_web_channel_invite_invalid_channel(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': 100**100, \
                                'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_invite_invalid_u_id(init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid u_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                            'u_id': 100**100}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_invite_invalid_token(init):    # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': 100**100, 'channel_id': chn1['channel_id'], \
                                    'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_details bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_details(init): # pylint: disable=redefined-outer-name
    '''
    Test for standard channel details
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }
        ]}


def test_web_channel_details_multiple(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard channel details for multiple users
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_details_invalid_channel(init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': 100**100,
    })
    req = f'{BASE_URL}/channel/details?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_details_not_member(init):  # pylint: disable=redefined-outer-name
    '''
    Test for user not member of channel
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_details_invalid_token(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    chn1 = init['chn1']

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': 100**100,
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_messages bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_messages_0(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard no messages
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    # Collecting channels messages
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
                'messages': [],
                'start': 0,
                'end': -1
                }


def test_web_channel_messages_2(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard 2 messages
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    # Add two messages and prepares expected output
    i = 0

    # Correct output
    correct_output = {
                'messages': [],
                'start': 0,
                'end': -1
                }
    while i < 2:
        data = json.dumps({'token': usr1['token'], \
            'channel_id': chn1['channel_id'], \
            'message': f'this is message {i}',}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/message/send", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req)

        # Takes note of messages to compare later
        correct_output['messages'].insert(0, {
            'message_id': i,
            'u_id': usr1['u_id'],
            'message': f'this is message {i}',
            'time_created': int(time.time()),
            'reacts': [],
            'is_pinned': 0
            })
        i = i + 1

    # Collecting channels messages
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == correct_output


def test_web_channel_messages_125(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard 125 messages
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    # Add two messages and prepares expected output
    i = 0

    # Correct output
    correct_output1 = {
                'messages': [],
                'start': 0,
                'end': 50
                }
    correct_output2 = {
                'messages': [],
                'start': 50,
                'end': 100
                }
    correct_output3 = {
                'messages': [],
                'start': 100,
                'end': -1
                }
    while i < 125:
        data = json.dumps({'token': usr1['token'], \
            'channel_id': chn1['channel_id'], \
            'message': f'this is message {i}',}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/message/send", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req)

        # Collects most recent 50
        if i > 74:
            correct_output1['messages'].insert(0, {
                'message_id': i,
                'u_id': usr1['u_id'],
                'message': f'this is message {i}',
                'time_created': int(time.time()),
                'reacts': [],
                'is_pinned': 0
                })
        # Collects center 50
        elif i > 24:
            correct_output2['messages'].insert(0, {
                'message_id': i,
                'u_id': usr1['u_id'],
                'message': f'this is message {i}',
                'time_created': int(time.time()),
                'reacts': [],
                'is_pinned': 0
                })
        # Collects last 25
        else:
            correct_output3['messages'].insert(0, {
                'message_id': i,
                'u_id': usr1['u_id'],
                'message': f'this is message {i}',
                'time_created': int(time.time()),
                'reacts': [],
                'is_pinned': 0
                })
        i = i + 1

    # Collecting channels messages
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'
    result = json.load(urllib.request.urlopen(req))
    assert result == correct_output1

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 50,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'
    result = json.load(urllib.request.urlopen(req))
    assert result == correct_output2

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 100,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'
    result = json.load(urllib.request.urlopen(req))
    assert result == correct_output3


def test_web_channel_messages_invalid_channel(init):    # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': 100**100,
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_messages_invalid_start(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid start, greater than message count
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
        'start': 100**100,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_messages_unauthorised_user(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid unauthorised user
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
        'channel_id': chn1['channel_id'],
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_messages_invalid_token(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    chn1 = init['chn1']

    query_string = urllib.parse.urlencode({
        'token': 100**100,
        'channel_id': chn1['channel_id'],
        'start': 0,
    })
    req = f'{BASE_URL}/channel/messages?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_leave bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_leave(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard channel leave
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}

    # usr2 leaving channel
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn1['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla',
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla',
            }
        ]}


def test_web_channel_leave_invalid_channel(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
        'channel_id': 100**100}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_leave_not_member(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user not member
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn1['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_leave_invalid_token(init):     # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    chn1 = init['chn1']

    data = json.dumps({'token': 'NOT_A_TOKEN', \
        'channel_id': chn1['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_join bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_join(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard channel join
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn2 = init['chn2']

    # usr2 joining channel
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn2['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn2['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz2',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_owner(init):   # pylint: disable=redefined-outer-name
    '''
    Test for owner joining private server
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn3 = init['chn3']

    # usr1 joining channel
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chn3['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
        'channel_id': chn3['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel NotIdriz',
        'owner_members': [
            {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }, {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }, {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }
        ]}


def test_web_channel_join_twice(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard joining twice
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn2 = init['chn2']

    # usr2 joins channel twice
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn2['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn2['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz2',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_join_input_error_joined(init):     # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
        'channel_id': 100**100}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_channel_join_access_error(init):   # pylint: disable=redefined-outer-name
    '''
    Test for private channel
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn1['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_channel_join_invalid_token(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    chn2 = init['chn2']

    data = json.dumps({'token': 'NOT_A_TOKEN', \
        'channel_id': chn2['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_addowner bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_addowner(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard addowner
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # Inviting usr2
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 added as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_addowner_not_member(init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard addowner, user not member
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 added as channel owner
    data = json.dumps({'token': usr1['token'], \
        'channel_id': chn1['channel_id'], 'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_addowner_invalid_channel(init):    # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']

    # usr2 added as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': 100**100, \
                                'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_addowner_user_already_owner(init):     # pylint: disable=redefined-outer-name
    '''
    Test for already owner
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 added as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_addowner_user_not_owner(init):     # pylint: disable=redefined-outer-name
    '''
    Test for caller isn't channel owner
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 added as channel owner
    data = json.dumps({'token': usr2['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_addowner_invalid_token(init):      # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 added as channel owner
    data = json.dumps({'token': 'NOT_A_TOKEN', 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for channel_removeowner bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_channel_removeowner(init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard removeowner
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 added as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 removed as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'channel_id': chn1['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel Idriz',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
            }, {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_removeowner_self(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard removeowner, slef
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn3 = init['chn3']

    # usr2 removed self as channel owner
    data = json.dumps({'token': usr2['token'], 'channel_id': chn3['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
        'channel_id': chn3['channel_id'],
    })
    req = f'{BASE_URL}/channel/details?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {
        'name': 'Channel NotIdriz',
        'owner_members': [],
        'all_members': [
            {
                'u_id': usr2['u_id'],
                'name_first': 'NotIdriz',
                'name_last': 'NotHaxhimolla'
            }
        ]}


def test_web_channel_removeowner_invalid_channel(init):     # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    usr2 = init['usr2']

    # usr2 removed as channel owner
    data = json.dumps({'token': usr1['token'], 'channel_id': 100**100, \
                                'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_removeowner_user_not_owner(init):      # pylint: disable=redefined-outer-name
    '''
    Test for not owner of channel
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr1 removed as channel owner
    data = json.dumps({'token': usr2['token'], 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_channel_removeowner_invalid_token(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    # usr2 removed as channel owner
    data = json.dumps({'token': 'NOT_A_TOKEN', 'channel_id': chn1['channel_id'], \
                                        'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner", data=data, \
                headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
