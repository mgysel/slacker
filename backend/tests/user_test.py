'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  06/03/2020
Description:    Testing functions in user.py
'''

import sys
import os
import pytest
from PIL import Image
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")


from error import AccessError, InputError   # pylint: disable=no-name-in-module, wrong-import-position
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle, usersAll, user_profile_upload_photo    # pylint: disable=import-error, wrong-import-position, line-too-long
from auth import auth_register  # pylint: disable=import-error, wrong-import-position

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
########## Tests for user_profile bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_profile(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for standard profile search
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)
    usr2 = auth_register('NotPerson@email.com', 'V3ryd!ff3r3nt@m3', 'NotIdriz', \
                                                    'NotHaxhimolla', USER_DATA)

    result = user_profile(usr1['token'], usr2['u_id'], USER_DATA)
    assert result["user"]['u_id'] == usr2['u_id'] and \
        result["user"]['email'] == 'NotPerson@email.com'


def test_profile_self(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for profile search on self
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    result = user_profile(usr['token'], usr['u_id'], USER_DATA)
    assert result["user"]['u_id'] == usr['u_id'] and \
        result["user"]['email'] == 'person@email.com'


def test_profile_invalid_u_id(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for profile search with invalid u_id
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile(usr1['token'], 100**100, USER_DATA)


def test_profile_invalid_token(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for profile search with invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr2 = auth_register('NotPerson@email.com', 'V3ryd!ff3r3nt@m3', 'NotIdriz', \
                                                    'NotHaxhimolla', USER_DATA)

    with pytest.raises(AccessError):
        user_profile('NotAToken', usr2['u_id'], USER_DATA)


'''
########## Tests for user_profile_setname below ##########
'''                                             # pylint: disable=pointless-string-statement
def test_user_profile_setname_working(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard setname
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    user_profile_setname(valid_credentials["token"], "Donald", \
                                                    "Trump", USER_DATA)

    profile = user_profile(valid_credentials["token"], \
                valid_credentials["u_id"], USER_DATA)

    assert profile["user"]["name_first"] == "Donald"
    assert profile["user"]["name_last"] == "Trump"


def test_user_profile_setname_inputerror1(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for name_first outside 1 to 50 character range
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    invalid_name_first = "x" * 51
    valid_name_last = "test_last_name"

    with pytest.raises(InputError):
        user_profile_setname(valid_credentials["token"], invalid_name_first, \
                                                valid_name_last, USER_DATA)


def test_user_profile_setname_inputerror2(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for name_last outside 1 to 50 character range
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    valid_name_first = "test_first_name"
    invalid_name_last = "x" * 51

    with pytest.raises(InputError):
        user_profile_setname(valid_credentials["token"], valid_name_first, \
                                            invalid_name_last, USER_DATA)


def test_user_profile_setname_inputerror3(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for name_first and/or name_last outside 1 to 50 character range
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    invalid_name_first = "x" * 51
    invalid_name_last = "x" * 51

    with pytest.raises(InputError):
        user_profile_setname(valid_credentials["token"], invalid_name_first, \
                                                invalid_name_last, USER_DATA)


def test_user_profile_setname_invalid_token(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        user_profile_setname('NOT_A_TOKEN', "Donald", \
                                    "Trump", USER_DATA)


'''
########## Tests for user_profile_setemail bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_user_profile_setemail_working(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard setname
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    user_profile_setemail(valid_credentials["token"], \
                            "test_email2@google.com", USER_DATA)

    profile = user_profile(valid_credentials["token"], \
                valid_credentials["u_id"], USER_DATA)

    assert profile["user"]["email"] == "test_email2@google.com"


def test_user_profile_setemail_inputerror1(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for invalid email given
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    valid_credentials = auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    an_invalid_email = "help.com"

    with pytest.raises(InputError):
        user_profile_setemail(valid_credentials["token"], \
                            an_invalid_email, USER_DATA)


def test_user_profile_setemail_inputerror2(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for email in use by another user
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    auth_register("test_email@google.com", \
        "a_random_test_password123", "Atest", "User", USER_DATA)

    user2 = auth_register("test_emai2l@google.com", \
        "a_random_test_password1232", "Atesttwo", "Usertwo", USER_DATA)

    with pytest.raises(InputError):
        user_profile_setemail(user2["token"], "test_email@google.com", USER_DATA)


def test_user_profile_setemail_invalid_token(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for invalid token given
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        user_profile_setemail('NOT_A_TOKEN', "Newemail@google.com", USER_DATA)


'''
########## Tests for user_profile_sethandle bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_handle(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for standard sethandle
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    user_profile_sethandle(usr['token'], 'IHax', USER_DATA)
    result = user_profile(usr['token'], usr['u_id'], USER_DATA)

    assert result['user']['handle_str'] == 'IHax'


def test_handle_invalid_handle_length_1(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where handle is not between 2 and 20 (inclusive)
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_sethandle(usr['token'], 'I', USER_DATA)


def test_handle_invalid_handle_length_2(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where handle is not between 3 and 20 (inclusive)
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_sethandle(usr['token'], \
            'Pneumonoultramicroscopicsilicovolcanoconiosis', USER_DATA)


def test_handle_taken_handle(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where the handle is already taken
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)
    user_profile_sethandle(usr1['token'], 'IHax', USER_DATA)

    usr2 = auth_register('NotPerson@email.com', 'V3ryd!ff3r3nt@m3', 'NotIdriz', \
                                                    'NotHaxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_sethandle(usr2['token'], 'IHax', USER_DATA)


def test_handle_invalid_token(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for sethandle where token is invalid
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        user_profile_sethandle('NotAToken', 'IHax', USER_DATA)


'''
########## Tests for usersAll bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_users_all_one(data_init):  # pylint: disable=redefined-outer-name
    '''
    Test for standard usersAll, reset so only one user is made
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    # Create authorized user, retrieve u_id and token
    first_name = "Mike"
    last_name = "Gysel"
    email = "mikegysel4321@gmail.com"
    token_uid = \
    auth_register(email, "ThisisPW1234!", first_name, last_name, USER_DATA)
    u_id = token_uid.get('u_id')
    token = token_uid.get('token')

    assert usersAll(token, USER_DATA) == \
        {
            'users': [
                {
                    'u_id': u_id,
                    'email': email,
                    'name_first': first_name,
                    'name_last': last_name,
                    'handle_str': f"{first_name.lower()}{last_name.lower()}",
                    'profile_img_url': ''
                }
            ]
        }


def test_users_all_multiple(data_init): # pylint: disable=redefined-outer-name
    '''
    Test for standard usersAll with multiple users
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    # Create two authorized user, retrieve u_id and token
    first_name_one = "Mike"
    last_name_one = "Gysel"
    email_one = "mikegysel4321@gmail.com"
    token_uid = \
    auth_register(email_one, "ThisisPW1234!", first_name_one, last_name_one, USER_DATA)
    u_one_id = token_uid.get('u_id')
    token_one = token_uid.get('token')

    first_name_two = "NotMike"
    last_name_two = "NotGysel"
    email_two = "mikegysel432@gmail.com"
    token_uid = \
    auth_register(email_two, "ThisisPW1234!", first_name_two, last_name_two, USER_DATA)
    u_two_id = token_uid.get('u_id')

    assert usersAll(token_one, USER_DATA) == \
        {
            'users': [
                {
                    'u_id': u_one_id,
                    'email': email_one,
                    'name_first': first_name_one,
                    'name_last': last_name_one,
                    'handle_str': \
                    f"{first_name_one.lower()}{last_name_one.lower()}",
                    'profile_img_url': ''
                }, {
                    'u_id': u_two_id,
                    'email': email_two,
                    'name_first': first_name_two,
                    'name_last': last_name_two,
                    'handle_str': \
                    f"{first_name_two.lower()}{last_name_two.lower()}",
                    'profile_img_url': ''
                }
            ]
        }


def test_users_all_invalid_token(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for usersAll with invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    with pytest.raises(AccessError):
        usersAll("NOTATOKEN", USER_DATA)


'''
########## Tests for user_profile_upload_photo below ##########
'''     #pylint: disable=pointless-string-statement

def test_photo_success(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo success
    NOTE: This function must be run from the root directory so that
    the filepaths are correct
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    img_url = \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg'

    # Upload photo
    x_start = 0
    y_start = 0
    x_end = 400
    y_end = 400
    user_profile_upload_photo(usr1['token'], img_url, x_start, y_start, \
        x_end, y_end, USER_DATA)

    # Check file exists
    print(os.getcwd())
    image_path = f"src/static/{usr1['u_id']}.jpg"
    assert os.path.exists(image_path)

    # Check file dimensions
    image = Image.open(image_path)
    width, height = image.size
    assert width == x_end - x_start
    assert height == y_end - y_start

    # Delete File
    os.remove(image_path)


def test_photo_invalid_url(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo with invalid url
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_upload_photo(usr1['token'], \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse1.jpg',\
        0, 0, 1, 1, USER_DATA)

def test_photo_not_jpg(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo with invalid file type
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_upload_photo(usr1['token'], 'dsaf43ad1s.tiff', 0, 0, \
        1, 1, USER_DATA)

def test_photo_invalid_size_incorrect_end(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo with invalid (x, y) crop coordinates
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_upload_photo(usr1['token'], \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg',\
        0, 0, 10000000, 10000000, USER_DATA)

def test_photo_invalid_size_incorrect_start(data_init):    # pylint: disable=redefined-outer-name
    '''
    Test for user_profile_upload_photo with invalid (x, y) crop coordinates
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth_register('person@email.com', 'V3ryG00d@m3', 'Idriz', \
                                            'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        user_profile_upload_photo(usr1['token'], \
        'https://onlinejpgtools.com/images/examples-onlinejpgtools/mouse.jpg',\
        -1, 0, 1, 1, USER_DATA)
