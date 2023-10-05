'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  08/03/2020
Description:    Testing functions in auth.py
'''
import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")

from error import InputError, AccessError   # pylint: disable=no-name-in-module, wrong-import-position
import auth     # pylint: disable=import-error, wrong-import-position


'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
@pytest.fixture
def data_init():
    '''
    Sets-up USER_DATA
    '''
    return {'num_users': 0, 'users': []}


'''
########## Tests for auth_regester bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_register(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard register
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    result = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)

    assert result['u_id'] is not None and result['u_id'] >= 0


def test_register_invalid_email(data_init):     # pylint: disable=redefined-outer-name
    '''
    Test for invalid email entered
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('not_an_email', 'V3ryG00d@m3', \
                            'Idriz', 'Haxhimolla', USER_DATA)


def test_register_email_used(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for already used email
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                        'Idriz', 'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryd!ff3r3nt@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)


def test_register_invalid_password(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for password less than 6 characters
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'bad', \
                        'Idriz', 'Haxhimolla', USER_DATA)


def test_register_invalid_first_1(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for first name not within 1 to 50 characters inclusive
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                    '', 'Haxhimolla', USER_DATA)


def test_register_invalid_first_2(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for first name not within 1 to 50 characters inclusive
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', \
        'IdrizAndPneumonoultramicroscopicsilicovolcanoconiosis', 'Haxhimolla', \
        USER_DATA)


def test_register_invalid_last_1(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for last name not within 1 to 50 characters inclusive
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                        'Idriz', '', USER_DATA)


def test_register_invalid_last_2(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for last name not within 1 to 50 characters inclusive
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
            'HaxhimollaAndPneumonoultramicroscopicsilicovolcanoconiosis', \
            USER_DATA)


def test_register_numbers_first(data_init):     # pylint: disable=redefined-outer-name
    '''
    Test for numbers in first name
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idri123z', \
                                                'Haxhimolla', USER_DATA)


def test_register_numbers_last(data_init):      # pylint: disable=redefined-outer-name
    '''
    Test for numbers in last name
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimoll123a', USER_DATA)


def test_register_empty(data_init):     # pylint: disable=redefined-outer-name
    '''
    Test for no data passed
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_register('', '', '', '', USER_DATA)


'''
########## Tests for auth_login bellow ##########
'''                                             # pylint: disable=pointless-string-statement
#Assumes auth.register() and auth_logout works
def test_login(data_init):      # pylint: disable=redefined-outer-name
    '''
    Test for standard login
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                            'Idriz', 'Haxhimolla', USER_DATA)
    auth.auth_logout(usr['token'], USER_DATA)
    result = auth.auth_login('person@email.com', 'V3ryG00d@m3', USER_DATA)

    assert usr['u_id'] == result['u_id']


def test_login_invalid_email(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for login with invalid email
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr = auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                                'Haxhimolla', USER_DATA)
    auth.auth_logout(usr['token'], USER_DATA)

    with pytest.raises(InputError):
        auth.auth_login('person.com', 'V3ryG00d@m3', USER_DATA)


def test_login_unregistered_email(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for login with unregistered email/user
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_login('person@email.com', 'V3ryG00d@m3', USER_DATA)


def test_login_invalid_password(data_init):     # pylint: disable=redefined-outer-name
    '''
    Test for login with invalid password
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr = auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                                'Haxhimolla', USER_DATA)
    auth.auth_logout(usr['token'], USER_DATA)

    with pytest.raises(InputError):
        auth.auth_login('person@email.com', 'NotPassword', USER_DATA)


def test_login_empty(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for login with no data
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(InputError):
        auth.auth_login('', '', USER_DATA)



'''
########## Tests for auth_logout bellow ##########
'''                                             # pylint: disable=pointless-string-statement
#Assumes auth.register(): and auth.login(): works
def test_logout(data_init):     # pylint: disable=redefined-outer-name
    '''
    Test for standard logout
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr = auth.auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                                'Haxhimolla', USER_DATA)
    result = auth.auth_logout(usr['token'], USER_DATA)

    assert result['is_success']


def test_logout_invalid_token(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for logout with invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        auth.auth_logout('NOT_A_TOKEN', USER_DATA)
