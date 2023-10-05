'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  27/03/2020
Description:    Testing functions in channel.py with Flask wrapping
'''
import urllib.request
import json
import pytest

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

    # Making channel
    data = json.dumps({'token': usr1['token'], 'name': 'Channel Idriz', \
        'is_public': False}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channels/create", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    chn1 = json.load(urllib.request.urlopen(req))

    return {'usr1': usr1, 'usr2': usr2, 'chn1': chn1}

def test_web_message_send(init): # pylint: disable=redefined-outer-name
    '''
    Test for standard message send
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    assert result['message_id'] >= 0 and result['message_id'] is not None


def test_web_message_send_input_too_long(init): # pylint: disable=redefined-outer-name
    '''
    Test for message over 1000 char long
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'*3000}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_message_send_invalid_channel(init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid channel_id
    '''
    # Prepairing data
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'channel_id': 100**100, \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_message_send_not_member(init): # pylint: disable=redefined-outer-name
    '''
    Test for user not channel member
    '''
    # Prepairing data
    usr2 = init['usr2']
    chn1 = init['chn1']

    data = json.dumps({'token': usr2['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'*3000}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_message_send_invalid_token(init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    # Prepairing data
    chn1 = init['chn1']

    data = json.dumps({'token': 100**100, 'channel_id': chn1['channel_id'], \
        'message': 'Hello'*3000}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_remove_working(init): # pylint: disable=redefined-outer-name
    '''
    Test that remove is working correctly
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/remove", \
        data=data2, headers={'Content-Type': 'application/json'}, method='DELETE')
    result2 = json.load(urllib.request.urlopen(req2))
    assert result2 == {}

def test_remove_inputerror(init): # pylint: disable=redefined-outer-name
    '''
    Test that input error is raised for test remove
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/remove", \
        data=data2, headers={'Content-Type': 'application/json'}, method='DELETE')
    json.load(urllib.request.urlopen(req2))

    req3 = urllib.request.Request(f"{BASE_URL}/message/remove", \
        data=data2, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_remove_accesserror(init): # pylint: disable=redefined-outer-name
    '''
    Test that accesserror is raised for test remove
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']
    usr2 = init['usr2']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr2['token'], 'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/remove", \
        data=data2, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_message_edit_working(init): # pylint: disable=redefined-outer-name
    '''
    Test message edit is working
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'message': 'THIS IS AN EDIT'}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/edit", \
        data=data2, headers={'Content-Type': 'application/json'}, method='PUT')
    result2 = json.load(urllib.request.urlopen(req2))
    assert result2 == {}

def test_message_edit_empty(init): # pylint: disable=redefined-outer-name
    '''
    Test message_remove is called if message field is empty
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'message': ''}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/edit", \
        data=data2, headers={'Content-Type': 'application/json'}, method='PUT')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], 'message_id': result['message_id']}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/remove", \
        data=data3, headers={'Content-Type': 'application/json'}, method='DELETE')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)


def test_edit_accesserror(init): # pylint: disable=redefined-outer-name
    '''
    Test that accesserror is raised for message_edit
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']
    usr2 = init['usr2']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr2['token'], 'message_id': result['message_id'], \
        'message': 'a hectic edit'}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/edit", \
        data=data2, headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_edit_accesserror2(init): # pylint: disable=redefined-outer-name
    '''
    Test that access error2 is being raised for message_edit
    '''
    # Preparing data
    usr1 = init['usr1']
    chn1 = init['chn1']
    usr2 = init['usr2']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr2['token'], \
        'channel_id': chn1['channel_id']}).encode('utf-8')
    urllib.request.Request(f"{BASE_URL}/channel/join", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')

    data3 = json.dumps({'token': usr2['token'], 'message_id': result['message_id'], \
        'message': 'An edit'}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/edit", \
        data=data3, headers={'Content-Type': 'application/json'}, method='PUT')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_message_reactworking(init): # pylint: disable=redefined-outer-name
    '''
    Test for reacting to a message
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    result2 = json.load(urllib.request.urlopen(req2))
    assert result2 == {}

def test_messagereact_inputerror1(init): # pylint: disable=redefined-outer-name
    '''
    Test for react message to raise input error - incorrect message_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': 3, \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_messagereact_inputerror2(init): # pylint: disable=redefined-outer-name
    '''
    Test for react message to raise input error - incorrect react_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 100}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_messagereact_inputerror3(init): # pylint: disable=redefined-outer-name
    '''
    Test for react message to raise input error - message has already been reacted
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    req3 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_message_unreactworking(init): # pylint: disable=redefined-outer-name
    '''
    Test for reacting to a message
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 0}).encode('utf-8')
    urllib.request.Request(f"{BASE_URL}/message/unreact", \
        data=data3, headers={'Content-Type': 'application/json'}, method='POST')

def test_messageunreact_inputerror1(init): # pylint: disable=redefined-outer-name
    '''
    Test for unreact message to raise input error - incorrect message_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], 'message_id': 78, \
        'react_id': 1}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/unreact", \
        data=data3, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_messageunreact_inputerror2(init): # pylint: disable=redefined-outer-name
    '''
    Test for unreact message to raise input error - incorrect react_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 1}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/react", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 345}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/unreact", \
        data=data3, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_messageunreact_inputerror3(init): # pylint: disable=redefined-outer-name
    '''
    Test for unreact message to raise input error - message has not been reacted
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], 'message_id': result['message_id'], \
        'react_id': 2}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/unreact", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_pinworking(init): # pylint: disable=redefined-outer-name
    '''
    Test for pinning a message
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    result2 = json.load(urllib.request.urlopen(req2))
    assert result2 == {}

def test_messagepin_inputerror1(init): # pylint: disable=redefined-outer-name
    '''
    Test for pin message to raise input error - incorrect message_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': 3}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_messagepin_inputerror2(init): # pylint: disable=redefined-outer-name
    '''
    Test for pin message to raise input error - message has already been pinned
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    req3 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_unpinworking(init): # pylint: disable=redefined-outer-name
    '''
    Test for unpinning a message
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/unpin", \
        data=data3, headers={'Content-Type': 'application/json'}, method='POST')
    result3 = json.load(urllib.request.urlopen(req3))
    assert result3 == {}

def test_messageunpin_inputerror1(init): # pylint: disable=redefined-outer-name
    '''
    Test for unpin message to raise input error - incorrect message_id
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    data3 = json.dumps({'token': usr1['token'], 'message_id': 100}).encode('utf-8')
    req3 = urllib.request.Request(f"{BASE_URL}/message/unpin", \
        data=data3, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req3)

def test_messageunpin_inputerror2(init): # pylint: disable=redefined-outer-name
    '''
    Test for unpin message to raise input error - message has already been unpinned
    '''
    # Prepairing data
    usr1 = init['usr1']
    chn1 = init['chn1']

    data = json.dumps({'token': usr1['token'], 'channel_id': chn1['channel_id'], \
        'message': 'Hello'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/message/send", \
        data=data, headers={'Content-Type': 'application/json'}, method='POST')
    result = json.load(urllib.request.urlopen(req))

    data2 = json.dumps({'token': usr1['token'], \
        'message_id': result['message_id']}).encode('utf-8')
    req2 = urllib.request.Request(f"{BASE_URL}/message/pin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req2))

    req3 = urllib.request.Request(f"{BASE_URL}/message/unpin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    json.load(urllib.request.urlopen(req3))

    req4 = urllib.request.Request(f"{BASE_URL}/message/unpin", \
        data=data2, headers={'Content-Type': 'application/json'}, method='POST')
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req4)
