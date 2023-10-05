'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  16/04/2020
Description:    Testing admin functions with Flask wrapping
'''
import urllib.request
import json
import pytest


'''
########## Helper function and variable used throughout tests ##########
'''                                             # pylint: disable=pointless-string-statement
BASE_URL = 'http://127.0.0.1:8889'

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
    chn = json.load(urllib.request.urlopen(req))

    return {'usr1': usr1, 'usr2': usr2, 'chn': chn}


'''
########## Tests for admin_userpermission_change bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_userpermission_change(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard changing of usrs permissions to owner
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn = init['chn']
    owner = 1

    # seting usr2 as owner
    data = json.dumps({'token': usr1['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 joining usr1 private channel
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Collecting channels details
    query_string = urllib.parse.urlencode({
        'token': usr2['token'],
        'channel_id': chn['channel_id'],
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


def test_web_userpermission_change_member_2(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard changing a usrs permissions to owner and back to member
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn = init['chn']
    owner = 1
    member = 2

    # seting usr2 as owner
    data = json.dumps({'token': usr1['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # seting usr2 as member
    data = json.dumps({'token': usr1['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': member}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # usr2 joining usr1 private channel
    data = json.dumps({'token': usr2['token'], \
        'channel_id': chn['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_userpermission_invalid_u_id(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid u_id
    '''
    usr1 = init['usr1']
    owner = 1

    # seting usr as owner
    data = json.dumps({'token': usr1['token'], 'u_id': 100**100, \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_userpermission_invalid_per_id(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid permission_id
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # seting usr2 permission_id
    data = json.dumps({'token': usr1['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': 100**100}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_userpermission_not_owner(init):   # pylint: disable=redefined-outer-name
    '''
    Test for calling user not being a owner
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']
    chn = init['chn']
    owner = 1
    member = 2

    # seting usr2 as owner
    data = json.dumps({'token': usr2['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_userpermission_invalid_token(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    usr2 = init['usr2']
    owner = 1

    # seting usr2 as owner
    data = json.dumps({'token': 'NOT_A_TOKEN', 'u_id': usr2['u_id'], \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for admin_user_remove bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_user_remove(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard deleting a user
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Removing usr2
    data = json.dumps({'token': usr1['token'], \
            'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')
    urllib.request.urlopen(req)

    # Attempting to login as usr2
    data = json.dumps({'email': 'NotPerson@email.com', \
        'password': 'V3ryd!ff3r3nt@m3'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_user_remove_2(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard deleting a owner user
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']
    owner = 1

    # seting usr2 as owner
    data = json.dumps({'token': usr1['token'], 'u_id': usr2['u_id'], \
                                    'permission_id': owner}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/userpermission/change", \
            data=data, headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req)

    # Removing usr2
    data = json.dumps({'token': usr1['token'], \
            'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')
    urllib.request.urlopen(req)

    # Attempting to login as usr2
    data = json.dumps({'email': 'NotPerson@email.com', \
        'password': 'V3ryd!ff3r3nt@m3'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
            headers={'Content-Type': 'application/json'}, method='POST')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_remove_invalid_u_id(init):   # pylint: disable=redefined-outer-name
    '''
    Test for removing a user twice
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Removing usr2
    data = json.dumps({'token': usr1['token'], \
            'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')
    urllib.request.urlopen(req)

    # Attempting to remove usr2
    data = json.dumps({'token': usr2['token'], \
            'u_id': usr1['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_remove_invalid_u_id_2(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid u_id
    '''
    usr1 = init['usr1']

    # Attempting to remove u_id 100**100
    data = json.dumps({'token': usr1['token'], \
            'u_id': 100**100}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_remove_not_owner(init):   # pylint: disable=redefined-outer-name
    '''
    Test for regular user calling function
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    # Attempting to remove usr1
    data = json.dumps({'token': usr2['token'], \
            'u_id': usr1['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_remove_invalid_token(init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    usr2 = init['usr2']

    # Attempting to remove usr2
    data = json.dumps({'token': 'NOT_A_TOKEN', \
            'u_id': usr2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/admin/user/remove", \
            data=data, headers={'Content-Type': 'application/json'}, method='DELETE')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
