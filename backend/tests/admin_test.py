'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  16/04/2020
Description:    Testing admin functions
'''
import sys
import pytest
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")

from error import InputError, AccessError   # pylint: disable=no-name-in-module, wrong-import-position
import auth     # pylint: disable=import-error, wrong-import-position
from other import admin_userpermission_change, admin_user_remove    # pylint: disable=import-error, wrong-import-position


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
########## Tests for admin_userpermission_change bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_userpermission_change(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard changing a usrs permissions to owner and back
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    owner = 1
    member = 2

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    admin_userpermission_change(usr1['token'], usr2['u_id'], owner, USER_DATA)
    assert USER_DATA['users'][1]['permission_id'] == owner

    admin_userpermission_change(usr1['token'], usr2['u_id'], member, USER_DATA)
    assert USER_DATA['users'][1]['permission_id'] == member


def test_userpermission_invalid_u_id(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid u_id
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    owner = 1

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        admin_userpermission_change(usr1['token'], 100**100, owner, USER_DATA)


def test_userpermission_invalid_per_id(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid permission_id
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    with pytest.raises(InputError):
        admin_userpermission_change(usr1['token'], usr2['u_id'], \
                                                100**100, USER_DATA)


def test_userpermission_not_owner(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for calling user not being a owner
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    owner = 1

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    with pytest.raises(AccessError):
        admin_userpermission_change(usr2['token'], usr2['u_id'], \
                                                    owner, USER_DATA)


def test_userpermission_invalid_token(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    owner = 1

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    with pytest.raises(AccessError):
        admin_userpermission_change('NOT_A_TOKEN', usr2['u_id'], \
                                                    owner, USER_DATA)


'''
########## Tests for admin_user_remove bellow ##########
'''                                             # pylint: disable=pointless-string-statement
def test_user_remove(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard deleting a user
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    admin_user_remove(usr1['token'], usr2['u_id'], USER_DATA)

    assert USER_DATA['users'][1]['u_id'] == usr2['u_id']
    assert USER_DATA['users'][1]['email'] == ''
    assert USER_DATA['users'][1]['password'] == ''
    assert USER_DATA['users'][1]['name_first'] == '[deleted]'
    assert USER_DATA['users'][1]['name_last'] == ''
    assert USER_DATA['users'][1]['handle_str'] == '[deleted]'
    assert USER_DATA['users'][1]['token'] == -1
    assert USER_DATA['users'][1]['reset_code'] == -1
    assert USER_DATA['users'][1]['permission_id'] == 0


def test_user_remove_2(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for standard deleting a owner user
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name
    owner = 1

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    admin_userpermission_change(usr1['token'], usr2['u_id'], owner, USER_DATA)
    admin_user_remove(usr1['token'], usr2['u_id'], USER_DATA)

    assert USER_DATA['users'][1]['u_id'] == usr2['u_id']
    assert USER_DATA['users'][1]['email'] == ''
    assert USER_DATA['users'][1]['password'] == ''
    assert USER_DATA['users'][1]['name_first'] == '[deleted]'
    assert USER_DATA['users'][1]['name_last'] == ''
    assert USER_DATA['users'][1]['handle_str'] == '[deleted]'
    assert USER_DATA['users'][1]['token'] == -1
    assert USER_DATA['users'][1]['reset_code'] == -1
    assert USER_DATA['users'][1]['permission_id'] == 0


def test_remove_invalid_u_id(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for removing a user twice
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    admin_user_remove(usr1['token'], usr2['u_id'], USER_DATA)

    with pytest.raises(InputError):
        admin_user_remove(usr1['token'], usr2['u_id'], USER_DATA)


def test_remove_invalid_u_id_2(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid u_id
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)

    with pytest.raises(InputError):
        admin_user_remove(usr1['token'], 100**100, USER_DATA)


def test_remove_not_owner(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for regular user calling function
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)
    usr2 = auth.auth_register('person2@email.com', 'V3ryG00d@m3', \
                                'NotIdriz', 'NotHaxhimolla', USER_DATA)

    with pytest.raises(AccessError):
        admin_user_remove(usr2['token'], usr1['u_id'], USER_DATA)


def test_remove_invalid_token(data_init):   # pylint: disable=redefined-outer-name
    '''
    Test for invalid token
    '''
    USER_DATA = data_init   # pylint: disable=invalid-name

    usr1 = auth.auth_register('person@email.com', 'V3ryG00d@m3', \
                                'Idriz', 'Haxhimolla', USER_DATA)

    with pytest.raises(AccessError):
        admin_user_remove('NOT_A_TOKEN', usr1['u_id'], USER_DATA)
