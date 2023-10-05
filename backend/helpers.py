'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  23/03/2020
Description:    Commonly used helper functions for slackr
'''
import re

def queryUserData(key, value, USER_DATA):   # pylint: disable=invalid-name
    '''
    Queries USER_DATA based on a key-value pair
    Returns first user with instance of key-value pair
    Returns empty dictionary if USER_DATA does not contain key-value pair
    '''
    return next((item for item in USER_DATA['users'] if \
        item[key] == value), {})


def isValidUser(key, value, USER_DATA):     # pylint: disable=invalid-name
    '''
    Checks if the token is valid.
    Returns true if valid, false otherwise
    '''
    return len(queryUserData(key, value, USER_DATA))


def valid_email(email):
    '''
    Checks that email is valid. Original code from:
    https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    (Note: small edits have been made to the code in prevent warnings)
    '''
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    # Compares email to regex format
    if re.search(regex, email):
        return True

    return False
