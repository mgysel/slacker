'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  24/03/2020
Description:    Testing functions in auth.py with Flask wrapping
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

    # Passing user data
    usr_data = {
        'email': 'person@gmail.com',
        'password': 'V3ryG00d@m3',
        'name_first': 'Idriz',
        'name_last': 'Haxhimolla'
        }

    return usr_data


'''
########## Tests for auth_regester bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_register(init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard register
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    assert usr['u_id'] is not None and usr['u_id'] >= 0


def test_web_register_invalid_email(init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid email entered
    '''
    init['email'] = 'person.com'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_used_email(init):     # pylint: disable=redefined-outer-name
    '''
    Test for already used email
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

    # Since all fields apart from email can be identical between users, resend request
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_invalid_password(init):       # pylint: disable=redefined-outer-name
    '''
    Test for password less than 6 characters
    '''
    init['password'] = 'no'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_invalid_first_1(init):    # pylint: disable=redefined-outer-name
    '''
    Test for first name not within 1 to 50 characters inclusive
    '''
    init['name_first'] = ''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_invalid_first_2(init):    # pylint: disable=redefined-outer-name
    '''
    Test for first name not within 1 to 50 characters inclusive
    '''
    init['name_first'] = 'IdrizAndPneumonoultramicroscopicsilicovolcanoconiosis'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_invalid_last_1(init):     # pylint: disable=redefined-outer-name
    '''
    Test for last name not within 1 to 50 characters inclusive
    '''
    init['name_last'] = ''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_invalid_last_2(init):     # pylint: disable=redefined-outer-name
    '''
    Test for last name not within 1 to 50 characters inclusive
    '''
    init['name_last'] = 'HaxhimollaAndPneumonoultramicroscopicsilicovolcanoconiosis'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_numbers_first(init):  # pylint: disable=redefined-outer-name
    '''
    Test for numbers in first name
    '''
    init['name_first'] = 'Id1r2i3z'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_register_numbers_last(init):   # pylint: disable=redefined-outer-name
    '''
    Test for numbers in last name
    '''
    init['name_last'] = 'Ha1xh2im3ol4la'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for auth_login bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_login(init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard login
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr['token']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, \
                            headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

    data = json.dumps({'email': init['email'], \
        'password': init['password']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
                            headers={'Content-Type': 'application/json'})
    result = json.load(urllib.request.urlopen(req))

    assert usr['u_id'] == result['u_id']


def test_web_login_invalid_email(init): # pylint: disable=redefined-outer-name
    '''
    Test for login with invalid email
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr['token']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, \
                            headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

    init['email'] = 'person.com'
    data = json.dumps({'email': init['email'], \
        'password': init['password']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_login_invalid_password(init):  # pylint: disable=redefined-outer-name
    '''
    Test for login with invalid password
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr['token']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, \
                            headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

    init['password'] = 'NotPassword'
    data = json.dumps({'email': init['email'], \
        'password': init['password']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


def test_web_login_unregistered_email(init):    # pylint: disable=redefined-outer-name
    '''
    Test for login with unregistered email/user
    '''
    data = json.dumps({'email': init['email'], \
        'password': init['password']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, \
                            headers={'Content-Type': 'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)


'''
########## Tests for auth_logout bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_web_logout(init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard logout
    '''
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=data, \
                            headers={'Content-Type': 'application/json'})
    usr = json.load(urllib.request.urlopen(req))

    data = json.dumps({'token': usr['token']}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, \
                            headers={'Content-Type': 'application/json'})
    result = json.load(urllib.request.urlopen(req))

    assert result['is_success']


def test_web_logout_invalid_token(init):
    '''
    Test for logout with invalid token
    '''
    init['token'] = 'NOT_A_TOKEN'
    data = json.dumps(init).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/logout", data=data, \
                            headers={'Content-Type': 'application/json'})
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
