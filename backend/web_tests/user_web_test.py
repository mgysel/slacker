'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Testing functions in user.py with Flask wrapping
'''

import os
import urllib.request
import json
from PIL import Image
import pytest


'''
########## Helper function and variable used throughout tests ##########
'''                                             # pylint: disable=pointless-string-statement
BASE_URL = 'http://127.0.0.1:2080'


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
########## Tests for user_profile bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_profile(init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard profile search
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr2['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['user']['u_id'] == usr2['u_id']


def test_web_profile_self(init):    # pylint: disable=redefined-outer-name
    '''
    Test for profile search on self
    '''
    usr1 = init['usr1']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['user']['u_id'] == usr1['u_id']


def test_web_profile_invalid_u_id(init):    # pylint: disable=redefined-outer-name
    '''
    Test for profile search with invalid u_id
    '''
    usr1 = init['usr1']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': 100**100,
    })
    req = f'{BASE_URL}/user/profile?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_profile_invalid_token(init):   # pylint: disable=redefined-outer-name
    '''
    Test for profile search with invalid token
    '''
    usr1 = init['usr1']

    query_string = urllib.parse.urlencode({
        'token': 'NOT_A_TOKEN',
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for user_profile_setname bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_setname(init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard setname
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name_first': 'New', \
                                'name_last': 'Name'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['user']['name_first'] == 'New'
    assert result['user']['name_last'] == 'Name'


def test_web_setname_invalid_name_first_1(init):    # pylint: disable=redefined-outer-name
    '''
    Test for name_first outside 1 to 50 character range
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name_first': '', \
                                'name_last': 'Name'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setname_invalid_name_first_2(init):    # pylint: disable=redefined-outer-name
    '''
    Test for name_first outside 1 to 50 character range
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name_first': 'O'*51, \
                                'name_last': 'Name'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setname_invalid_name_last_1(init):     # pylint: disable=redefined-outer-name
    '''
    Test for name_last outside 1 to 50 character range
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name_first': 'New', \
                                'name_last': ''}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setname_invalid_name_last_2(init):     # pylint: disable=redefined-outer-name
    '''
    Test for name_last outside 1 to 50 character range
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], 'name_first': 'New', \
                                'name_last': 'O'*51}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setname_invalid_token():
    '''
    Test for invalid token
    '''
    data = json.dumps({'token': 'NOT_A_TOKEN', 'name_first': 'New', \
                                'name_last': 'Name'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setname", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for user_profile_setemail bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_setemail(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard setname
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
                    'email': 'newemail@gmail.com'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['user']['email'] == 'newemail@gmail.com'


def test_web_setemail_invalid_email(init):      # pylint: disable=redefined-outer-name
    '''
    Test for invalid email given
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
                    'email': 'person.com'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setemail_email_used(init):     # pylint: disable=redefined-outer-name
    '''
    Test for email in use by another user
    '''
    usr1 = init['usr1']

    # usr2 email used (see email in init() function)
    data = json.dumps({'token': usr1['token'], \
                    'email': 'NotPerson@email.com'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_setemail_invalid_token():
    '''
    Test for invalid token given
    '''
    # usr2 email used (see email in init() function)
    data = json.dumps({'token': 'NOT_A_TOKEN', \
                    'email': 'newemail@email.com'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/setemail", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for user_profile_sethandle bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_handle(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard sethandle
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
                    'handle_str': 'IHax'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result['user']['handle_str'] == 'IHax'


def test_web_handle_invalid_handle_length_1(init):  # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where handle is not between 2 and 20 (inclusive)
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
                    'handle_str': 'I'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_handle_invalid_handle_length_2(init):  # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where handle is not between 3 and 20 (inclusive)
    '''
    usr1 = init['usr1']

    data = json.dumps({'token': usr1['token'], \
                    'handle_str': 'I'*21}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_handle_taken_handle(init):     # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where the handle is already taken
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    data = json.dumps({'token': usr1['token'], \
                    'handle_str': 'IHax'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')
    urllib.request.urlopen(req)

    data = json.dumps({'token': usr2['token'], \
                    'handle_str': 'IHax'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_handle_invalid_token():
    '''
    Test for sethandle where token is invalid
    '''
    data = json.dumps({'token': 'NOT_A_TOKEN', \
                    'handle_str': 'IHax'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/sethandle", data=data, \
                    headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for usersAll bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_usersall():
    '''
    Test for standard usersAll, reset so only one user is made
    '''
    urllib.request.urlopen(f"{BASE_URL}/workspace/reset", data={})

    usr_data = json.dumps({
                'email': 'person@gmail.com',
                'password': 'V3ryG00d@m3',
                'name_first': 'Idriz',
                'name_last': 'Haxhimolla'
                }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=usr_data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    query_string = urllib.parse.urlencode({
        'token': usr['token'],
    })
    req = f'{BASE_URL}/users/all?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {'users': [{
        'u_id': usr['u_id'],
        'email': 'person@gmail.com',
        'name_first': 'Idriz',
        'name_last': 'Haxhimolla',
        'handle_str': 'idrizhaxhimolla'
        }]}


def test_usersall_multiple(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard usersAll with multiple users
    '''
    usr1 = init['usr1']
    usr2 = init['usr2']

    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
    })
    req = f'{BASE_URL}/users/all?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert result == {'users': [{
        'u_id': usr1['u_id'],
        'email': 'person@gmail.com',
        'name_first': 'Idriz',
        'name_last': 'Haxhimolla',
        'handle_str': 'idrizhaxhimolla'
        }, {
            'u_id': usr2['u_id'],
            'email': 'NotPerson@email.com',
            'name_first': 'NotIdriz',
            'name_last': 'NotHaxhimolla',
            'handle_str': 'notidriznothaxhimoll'
        }]}


def test_usersall_invalid_token():
    '''
    Test for usersAll with invalid token
    '''

    query_string = urllib.parse.urlencode({
        'token': 'NOT_A_TOKEN',
    })
    req = f'{BASE_URL}/users/all?{query_string}'

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_upload_photo_success(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo success
    NOTE: This function must be run from the root directory so that
    the filepaths are correct
    '''
    x_start = 0
    y_start = 0
    x_end = 100
    y_end = 100

    usr1 = init['usr1']
    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg'

    # Update photo
    data = json.dumps({'token': usr1['token'], 'img_url': img_url, \
        'x_start': x_start, 'y_start': y_start, 'x_end': x_end, \
        'y_end': y_end}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/uploadphoto", \
        data=data, \
        headers={'Content-Type': 'application/json'}, method='PUT')
    result = json.load(urllib.request.urlopen(req))

    # Check file exists
    image_path = f"src/static/{usr1['u_id']}.jpg"

    # Check file dimensions
    image = Image.open(image_path)
    width, height = image.size
    assert width == x_end - x_start
    assert height == y_end - y_start

    # Check url of file
    query_string = urllib.parse.urlencode({
        'token': usr1['token'],
        'u_id': usr1['u_id'],
    })
    req = f'{BASE_URL}/user/profile?{query_string}'
    result = json.load(urllib.request.urlopen(req))

    assert os.path.exists(image_path)

    # Remove file
    os.remove(image_path)

    assert result['user']['profile_img_url'] == f"/static/{usr1['u_id']}.jpg"


def test_web_upload_photo_invalid_url(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo
    Input Error: invalid url
    '''
    usr1 = init['usr1']
    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse1.jpg'

    data = json.dumps({'token': usr1['token'], 'img_url': img_url, \
        'x_start': 0, 'y_start': 0, 'x_end': 1, 'y_end': 1}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/uploadphoto", \
        data=data, \
        headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_upload_photo_not_jpg(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo
    Input Error: Image url not a jpg
    '''
    usr1 = init['usr1']
    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.tiff'

    data = json.dumps({'token': usr1['token'], 'img_url': img_url, \
        'x_start': 0, 'y_start': 0, 'x_end': 1, 'y_end': 1}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/uploadphoto", \
        data=data, \
        headers={'Content-Type': 'application/json'}, method='PUT')



    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_upload_photo_incorrect_start(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo
    Input Error: Incorrect start (x, y) coordinates
    '''
    usr1 = init['usr1']
    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg'

    data = json.dumps({'token': usr1['token'], 'img_url': img_url, \
        'x_start': -1, 'y_start': -1, 'x_end': 1, 'y_end': 1}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/uploadphoto", \
        data=data, \
        headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_upload_photo_incorrect_end(init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo
    Input Error: Incorrect end (x, y) coordinates
    '''
    usr1 = init['usr1']
    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg'

    data = json.dumps({'token': usr1['token'], 'img_url': img_url, \
        'x_start': 0, 'y_start': 0, 'x_end': 1000000, 'y_end': 1000000\
        }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/user/profile/uploadphoto", \
        data=data, \
        headers={'Content-Type': 'application/json'}, method='PUT')

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
