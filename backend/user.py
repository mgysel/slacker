'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Profile, Set Name, Set Email, Set Handle functions for slackr
'''

import os
from io import BytesIO
import urllib.request
from PIL import Image
from helpers import queryUserData, isValidUser, valid_email
from error import AccessError, InputError
from objects.userObject import User

'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def user_profile(token, u_id):       # pylint: disable=invalid-name
    '''
    Checks if the user with u_id is valid
    If valid, returns info about u_id, email, name, handle
    If not valid, raises InputError
    '''
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    if user['u_id'] != u_id:
        raise InputError('u_id is not valid!')

    user_info = {
        'u_id': user['u_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url']
    }

    return user_info

def user_profile_setname(token, name_first, name_last):  # pylint: disable=invalid-name
    '''
    Updates the authorised user's first and last names
    InputError if names not valid
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    # Check and update name_first
    if is_valid_name(name_first):
        User.update_user_attribute('token', token, 'name_first', name_first)
    else:
        raise InputError('First name is invalid!')

    if is_valid_name(name_last):
        User.update_user_attribute('token', token, 'name_last', name_last)
    else:
        raise InputError('Last name is invalid!')

    return {}


def user_profile_setemail(token, email):     # pylint: disable=invalid-name
    '''
    Updates the authorised user's email
    InputError if email not valid or unique
    '''
    # Check if valid user
    user1 = User.find_user_by_attribute('token', token)
    if user1 is None:
        raise AccessError('Invalid token!')

    if not valid_email(email):
        raise InputError('Invalid email!')

    user2 = User.find_user_by_attribute('email', email)
    if user2 is not None and user1['u_id'] != user2['u_id']:
        raise InputError('Email taken!')

    User.update_user_attribute('token', token, 'email', email)

    return {}

def user_profile_sethandle(token, handle_str):   # pylint: disable=invalid-name
    '''
    Updates the authorised user's handle
    InputError if handle not valid or unique
    '''
    # Check if valid user
    user1 = User.find_user_by_attribute('token', token)
    if user1 is None:
        raise AccessError('Invalid token!')

    if not is_valid_handle(handle_str):
        raise InputError('Handle is not between 2 and 20 characters!')

    if handle_str == '[deleted]':
        raise InputError('Handle can\'t be [deleted]!')

    user2 = User.find_user_by_attribute('handle_str', handle_str)
    if user2 is not None and user1['u_id'] != user2['u_id']:
        raise InputError('Handle is taken!')

    User.update_user_attribute('token', token, 'handle_str', handle_str)

    return {}

def usersAll(token):     # pylint: disable=invalid-name
    '''
    Returns a list of all users and their associated details.
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')

    all_users = {'users': []}
    users = User.get_all_users()
    for user in users:
        all_users['users'].append(
            {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url']
            }
        )

    return all_users

def user_profile_upload_photo(token, img_url, x_start, y_start, x_end, y_end, BACKEND_URL):     # pylint: disable=too-many-arguments
    '''
    Given url of an image, crops the image within the bounds(x, y)
    Input error when not a jpeg, not within (x, y) dimensions, or
    img_url returns an HTTP status other than 200
    '''
    # Check if valid user
    user = User.find_user_by_attribute('token', token)
    if user is None:
        raise AccessError('Invalid token!')
    
    if not img_url.endswith('jpg') and not img_url.endswith('jpeg') \
            and not img_url.endswith('png') and not img_url.endswith('svg') \
            and not img_url.endswith('tiff'):
        raise InputError('Image uploaded is not a jpeg, png, svg or tiff!')

    # Get image from image url, crop
    try:
        img_filename = f"static/{user['u_id']}.{img_url.split('.')[-1]}"
        print("img_filename", img_filename)
        urllib.request.urlretrieve(img_url, img_filename)
        print("Inside urllib.request")
        # Open image if 200 response code
        img = Image.open(img_filename)
        print("Opened img: ", img)
        width, height = img.size

        x_start = int(x_start)
        y_start = int(y_start)
        x_end = int(x_end)
        y_end = int(y_end)

        # Check if valid (x, y) values
        if (x_start < 0) or (y_start < 0) or \
            (x_end > (x_start + width)) or (y_end > (y_start + height)):
            raise InputError('Any of x_start, y_start, x_end, y_end are not \
                within the dimensions of the image at the URL.')

        # Crop Image
        cropped_image = img.crop([x_start, y_start, x_end, y_end])
        print("Cropped img: ", cropped_image)
        cropped_image.save(img_filename)

        # profile_img_url = f'/static/{u_id}.jpg'
        # Save cropped image url in user database
        profile_img_url = f'{BACKEND_URL}/static/{user["u_id"]}.{img_url.split(".")[-1]}'
        User.update_user_attribute('token', token, 'profile_img_url', profile_img_url)

        # Update user profile_img_url
        # User.update_user_attribute('token', token, 'profile_img_url', profile_img_url)

    except urllib.error.HTTPError as e:     # pylint: disable=unused-variable
        raise InputError('img_url returns an HTTP status other than 200: ', e)

    return {}

'''
########## Helper functions ##########
'''

def is_valid_name(name):
    '''
    Returns False if name length between 1 and 50 characters inclusive and
    ensures name can't be '[deleted]'
    Returns True otherwise
    '''
    if len(name) < 1 or len(name) > 50:     # pylint: disable=len-as-condition
        return False

    if any(char.isdigit() for char in name):
        return False

    if name == '[deleted]':
        return False

    return True

def is_unique_email(email, USER_DATA):        # pylint: disable=invalid-name
    '''
    Checks if email already in use by an existing user
    Returns True (num > 0) if not in use, Returns False (num = 0) otherwise
    '''
    return not len(queryUserData('email', email, USER_DATA))    # pylint: disable=len-as-condition

def is_valid_handle(handle_str):
    '''
    Returns True if handle_str length between 2 and 20 characters inclusive and
    ensures handle can't be '[deleted]'
    Returns False otherwise
    '''

    return len(handle_str) >= 2 and len(handle_str) <= 20

def is_unique_handle(handle_str, USER_DATA):      # pylint: disable=invalid-name
    '''
    Checks if handle already in use by an existing user
    Returns True (num > 0) if not in use, Returns False (num = 0) otherwise
    '''
    return not len(queryUserData('handle_str', handle_str, USER_DATA))  # pylint: disable=len-as-condition