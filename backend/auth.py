'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  10/04/2020
Description:    Register, login and logout functions for slackr
'''
import hashlib
from random import randint
import smtplib
import ssl
from helpers import valid_email, queryUserData, isValidUser
from error import AccessError, InputError
from objects.userObject import User
from flask import Flask, request, redirect, url_for, make_response, jsonify
from json import dumps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta


'''
########## Main functions ##########
'''                      

def auth_login(email, password):     # pylint: disable=invalid-name
    '''
    Takes in a password, and email then searches user data for a match, if
    found will generate a token and mark user as logged in
    '''
    # Check email is valid
    if not valid_email(email):
        raise InputError('Email or Password is Invalid!')

    # Check Email belongs to a user
    user = User.find_user_by_attribute('email', email)
    print("User: ", user)
    if user is None:
        raise InputError('Email is Invalid!')

    # Check password is correct
    if hash_string(password) != user['password']:
        raise InputError('Password is Invalid!')

    # Get u_id
    user_id = user['_id']

    # Generate token
    tok = gen_string()
    # Update token for user
    User.update_user_attribute('email', email, 'token', tok)

    return {
        'u_id': str(user_id),
        'token': tok,
    }

def auth_register(email, password, name_first, name_last):       # pylint: disable=invalid-name
    '''
    Using the data passed in attempts to make a new user.
    Errors from invalid email, email taken, password < 6 characters,
    first or last name being ouside of 1 to 50 range
    (can be 1 or 50 characters long), numbers in first or last name
    '''
    # Checks email is valid and unused
    if not valid_email(email):
        raise InputError(description='Email is invalid!')

    # Check if email already used
    if not User.unused_email(email):
        raise InputError(description='Email is taken!')

    # Checks password is < 6 characters
    if len(password) < 6:
        raise InputError(description='Password too short!')

    # Checks first and last name are within length restrictions
    if len(name_first) not in range(1, 51):
        raise InputError(description='First name outside of 1 to 50 range!')

    if len(name_last) not in range(1, 51):
        raise InputError(description='Last name outside of 1 to 50 range!')

    # Checks first and last name don't contain numbers
    for char in name_first:
        if char.isdigit() is True:
            raise InputError(description='First name contains numbers!')

    for char in name_last:
        if char.isdigit() is True:
            raise InputError(description='Last name contains numbers!')

    # Checks first and last name aren't [deleted]
    if name_first == '[deleted]':
        raise InputError(description='First name can\'t be [deleted]!')

    if name_last == '[deleted]':
        raise InputError(description='Last name can\'t be [deleted]!')

    # Generates dictionary for new users info
    new_user = {}

    new_user['email'] = email
    new_user['password'] = hash_string(password)
    new_user['name_first'] = name_first
    new_user['name_last'] = name_last
    new_user['handle_str'] = gen_handle(name_first, name_last)
    new_user['profile_img_url'] = ''
    new_user['token'] = gen_string()
    # Code used to reset password, -1 means not requested
    new_user['reset_code'] = -1

    # First user has permission_id 1 (owner of slackr) else 2 (regular member)
    # if new_user['u_id'] == 0:
    #     new_user['permission_id'] = 1
    # else:
    #     new_user['permission_id'] = 2
    new_user['permission_id'] = 2

    # Add user to database
    user = User(
        None, 
        new_user['email'], 
        new_user['password'], 
        new_user['name_first'], 
        new_user['name_last'], 
        new_user['handle_str'], 
        new_user['profile_img_url'],
        new_user['token'],
        new_user['reset_code'], 
        new_user['permission_id']
    )
    user_id = User.insert_one(user)
    print("AUTH_REGISTER user_id: ", user_id)

    # Returns u_id and token of new user without other data
    return {
        'u_id': str(user_id),
        'token': new_user['token'],
    }

def auth_logout(token):      # pylint: disable=invalid-name
    '''
    Given a users token it will search through USER_DATA and invalidate the
    the token logging the user out
    '''

    # -1 means logged-out hence AccessError
    if token == -1:
        raise AccessError(description='Invalid token given!')

    else:
        # Update user_token to -1
        user = User.find_user_by_attribute('token', token)
        if user is None:
            raise AccessError(description='Invalid token given!')
        User.update_user_attribute('token', token, 'token', -1)

    return {
        'is_success': True
        }

def auth_request(email):       # pylint: disable=invalid-name
    '''
    Using the data passed in searches for user, if found will file a password
    request for user and send code to users email
    '''
    # Checks user email is valid and gathers user data
    user = User.find_user_by_attribute('email', email)
    if user is None:
        # This is done so users emails can't be discovered using reset page
        return {}

    # Generates a string and sets it as reset code
    reset_code = gen_string()
    User.update_user_attribute('email', email, 'reset_code', reset_code)

    # Sends email using TLC encryption
    port = 587
    smtp_server = 'smtp.gmail.com'
    sender = 'pyjamasemail@gmail.com'
    password = 'P1j@m@$%'

    message = f'''\
    Subject: Password Reset

    Hi there {user['name_first']},
    This is your code: {reset_code}'''

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender, password)
        server.sendmail(sender, email, message)

    return {}

def auth_reset(reset_code, new_password, USER_DATA):       # pylint: disable=invalid-name
    '''
    Using the data passed in searches for user with the same reset code, if
    found will set password to new password, else will return error
    '''
    # Checks reset code is valid
    if reset_code == -1:
        raise InputError(description='Reset Code is Invalid!')

    # if not valid_user('reset_code', reset_code, USER_DATA):
    #     raise InputError(description='Reset Code is Invalid!')

    # Checks password is valid
    if len(new_password) < 6:
        raise InputError(description='Password too short!')

    # Collects user data and changes password
    usr = queryUserData('reset_code', reset_code, USER_DATA)

    usr['password'] = hash_string(new_password)
    usr['reset_code'] = -1

    return {}

'''
########## Helper functions ##########
'''                                             # pylint: disable=pointless-string-statement
def hash_string(string):
    '''
    Takes in a string and returns the sha256 hash for that string
    '''
    return hashlib.sha256(string.encode()).hexdigest()


def gen_string():
    '''
    Generates a random string, by hashing a large number generated from the
    random library
    '''
    # Uses random to generate a large number
    token_base = randint(1, 100**100) + (27**100 * randint(-100**100, 100**100))

    return hash_string(str(token_base))

def gen_handle(name_first, name_last):       # pylint: disable=invalid-name
    '''
    Generates a handle for the user composed of the lower case first and last
    name combined. Will only take upto 20 characters then check if taken. If
    taken it will change the last 5 char to randomly generated number, if it
    is still taken then it will call itself and redo the process.
    '''
    if len(name_first) < 20:
        handle = name_first.lower()
    else:
        handle = name_first.lower()[:20]

    for char in name_last.lower():
        handle = handle + char
        if len(handle) >= 20:
            break

    # TODO: Check if unique handle

    return handle

# def unique_handle(handle, USER_DATA):       # pylint: disable=invalid-name
#     '''
#     Checks if a handle is unique or taken
#     '''
#     for usr in USER_DATA['users']:
#         if handle == usr['handle_str']:
#             return False

#     return True