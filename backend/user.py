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

'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def updateData(token, key, value, USER_DATA):   # pylint: disable=invalid-name
    '''
    Updates a value in USER_DATA given a key and valid token
    '''
    for user in USER_DATA['users']:
        if user['token'] == token:
            user[key] = value

def userfromtoken(token, USER_DATA):    # pylint: disable=invalid-name
    '''
    Takes in a token and returns the user that corresponds to that token. If
    none ar efound returns None
    '''
    for user in USER_DATA['users']:
        if user['token'] == token:
            return user
    return None


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


'''
########## Main functions ##########
'''                                             # pylint: disable=pointless-string-statement
def user_profile(token, u_id, USER_DATA):       # pylint: disable=invalid-name
    '''
    Checks if the user with u_id is valid
    If valid, returns info about u_id, email, name, handle
    If not valid, raises InputError
    '''
    if isValidUser('token', token, USER_DATA):
        if isValidUser('u_id', u_id, USER_DATA):
            result = queryUserData('u_id', u_id, USER_DATA)

            # Returns only all data except password and token
            user_info = {'user': {'u_id': result['u_id'],
                                  'email': result['email'],
                                  'name_first': result['name_first'],
                                  'name_last': result['name_last'],
                                  'handle_str': result['handle_str'],
                                  'profile_img_url': result['profile_img_url']
                                  }}

        else:
            raise InputError(f'{u_id} is not a valid user!')
    else:
        raise AccessError('Invalid token!')

    return user_info


def user_profile_setname(token, name_first, name_last, USER_DATA):  # pylint: disable=invalid-name
    '''
    Updates the authorised user's first and last names
    InputError if names not valid
    '''
    # Check if valid user
    if isValidUser('token', token, USER_DATA):

        # Check and update name_first
        if is_valid_name(name_first):
            updateData(token, 'name_first', name_first, USER_DATA)
        else:
            raise InputError('First name is invalid!')

        # Check and update name_last
        if is_valid_name(name_last):
            updateData(token, 'name_last', name_last, USER_DATA)
        else:
            raise InputError('First name is invalid!')
    else:
        raise AccessError('Invalid token!')

    return {}


def user_profile_setemail(token, email, USER_DATA):     # pylint: disable=invalid-name
    '''
    Updates the authorised user's email
    InputError if email not valid or unique
    '''
    if isValidUser('token', token, USER_DATA):
        if not valid_email(email):
            raise InputError('Invalid email!')

        if not is_unique_email(email, USER_DATA):
            raise InputError('Email taken!')

        else:
            return updateData(token, 'email', email, USER_DATA)
    else:
        raise AccessError('Invalid token!')

    return {}


def user_profile_sethandle(token, handle_str, USER_DATA):   # pylint: disable=invalid-name
    '''
    Updates the authorised user's handle
    InputError if handle not valid or unique
    '''
    if isValidUser('token', token, USER_DATA):
        if not is_valid_handle(handle_str):
            raise InputError('Handle is not between 2 and 20 characters!')

        if handle_str == '[deleted]':
            raise InputError('Handle can\'t be [deleted]!')

        if not is_unique_handle(handle_str, USER_DATA):
            raise InputError('Handle is taken!')
        else:
            return updateData(token, 'handle_str', handle_str, USER_DATA)
    else:
        raise AccessError('Invalid token!')

    return {}


def usersAll(token, USER_DATA):     # pylint: disable=invalid-name
    '''
    Returns a list of all users and their associated details.
    '''
    if isValidUser('token', token, USER_DATA):
        all_users = {'users': []}

        # Removes sensitive data before returning
        for usr in USER_DATA['users']:
            all_users['users'].append({'u_id': usr['u_id'],
                                       'email': usr['email'],
                                       'name_first': usr['name_first'],
                                       'name_last': usr['name_last'],
                                       'handle_str': usr['handle_str'],
                                       'profile_img_url': usr['profile_img_url']
                                       })

    else:
        raise AccessError('Invalid token!')

    return all_users


def user_profile_upload_photo(token, img_url, x_start, y_start, x_end, y_end, USER_DATA):     # pylint: disable=too-many-arguments
    '''
    Given url of an image, crops the image within the bounds(x, y)
    Input error when not a jpeg, not within (x, y) dimensions, or
    img_url returns an HTTP status other than 200
    '''
    if isValidUser('token', token, USER_DATA):
        # Check if valid image type
        if not img_url.endswith('jpg'):
            raise InputError('Image uploaded is not a jpeg')

        # Get image from image url, crop
        try:
            with urllib.request.urlopen(img_url) as response:
                # Open image if 200 response code
                image = Image.open(BytesIO(response.read()))
                width, height = image.size

                x_start = int(x_start)
                y_start = int(y_start)
                x_end = int(x_end)
                y_end = int(y_end)

                # Check if valid (x, y) values
                if (x_start < 0) or (y_start < 0) or \
                    (x_end > (x_start + width)) or (y_end > (y_start + height)):
                    raise InputError('Any of x_start, y_start, x_end, y_end are not \
                        within the dimensions of the image at the URL.')

                # Crop/Save image
                cropped_image = image.crop([x_start, y_start, x_end, y_end])
                u_id = userfromtoken(token, USER_DATA)['u_id']
                cropped_image.save(f"src/static/{u_id}.jpg")

                profile_img_url = f'/static/{u_id}.jpg'

                return updateData(token, 'profile_img_url', profile_img_url, USER_DATA)

        except urllib.error.HTTPError as e:     # pylint: disable=unused-variable
            raise InputError('img_url returns an HTTP status other than 200')

    else:
        raise AccessError('Invalid token!')

    return {}
