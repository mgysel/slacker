'''
Team:           Pyjamas
Tutorial:       W15A
Last Modified:  08/03/2020
Description:    Testing functions in channel.py
'''

import sys
sys.path.append(".")
sys.path.append("..")
sys.path.append("./src")

import pytest
from error import AccessError, InputError
from auth import auth_register
from channel import channel_invite, channel_messages, channel_join, channel_leave, channel_details, channel_addowner, channel_removeowner
from channels import channels_create
from message import message_send
import time

'''
########## Helper functions ##########
'''
@pytest.fixture
def user_data_init():
    return {'num_users': 0, 'users': []}


@pytest.fixture
def channel_data_init():
    return {'num_channels': 0, 'channels': []}


@pytest.fixture
def message_data_init():
    return {'channels': []}


'''
########## Tests for channel_invite bellow ##########
'''
#without an error
def test_channel_invite(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', False, CHANNEL_DATA, USER_DATA)

    channel_invite(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)
    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


#without an error
def test_channel_invite_twice(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', False, CHANNEL_DATA, USER_DATA)

    channel_invite(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)
    channel_invite(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)
    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


#input error when channel isn't valid
def test_channel_invite_invalid_channel(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_invite(usr1['token'], 100**100, usr2['u_id'], CHANNEL_DATA, USER_DATA)

#input error when user doesnt exist (invalid u_id)
def test_channel_invite_user_not_member(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_invite(usr1['token'], chnl['channel_id'], 100**100, CHANNEL_DATA, USER_DATA)


#access error invalid token
def test_channel_invite_invalid_token(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_invite('NOT_A_TOKEN', chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)


'''
########## Tests for channel_details bellow ##########
'''
# Correct channel_details test with one member
def test_channel_details_correct_one_member(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr['token'],'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    assert channel_details(usr['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {
        'name': 'Mikes channel',
        'owner_members': [
            {
                'u_id': usr['u_id'],
                'name_first': 'Mike',
                'name_last': 'Gysel',
            }
        ],
        'all_members': [
            {
                'u_id': usr['u_id'],
                'name_first': 'Mike',
                'name_last': 'Gysel',
            }
        ],
    }



def test_channel_details_correct_multiple_members(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('onelast@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    usr2 = auth_register('twolast@gmail.com', 'ThisisPW1234!', 'two', 'two', USER_DATA)

    chnl = channels_create(usr1['token'],'Ones channel', True, CHANNEL_DATA, USER_DATA)
    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    assert channel_details(usr1['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {
        'name': 'Ones channel',
        'owner_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'one',
                'name_last': 'one',
            }
        ],
        'all_members': [
            {
                'u_id': usr1['u_id'],
                'name_first': 'one',
                'name_last': 'one',
            },
            {
                'u_id': usr2['u_id'],
                'name_first': 'two',
                'name_last': 'two',
            },
        ],
    }


# Input Error: channel_id is not a valid channel 
def test_channel_details_input_error(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('onelast@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    usr2 = auth_register('twolast@gmail.com', 'ThisisPW1234!', 'two', 'two', USER_DATA)

    chnl = channels_create(usr1['token'],'Ones channel', True, CHANNEL_DATA, USER_DATA)
    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_details(usr1['token'], 100**100, CHANNEL_DATA, USER_DATA)    

# Access Error: authorized user is not a member of channel with channel_id
def test_channel_details_access_error(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('onelast@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    usr2 = auth_register('twolast@gmail.com', 'ThisisPW1234!', 'two', 'two', USER_DATA)

    chnl = channels_create(usr1['token'],'Ones channel', True, CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_details(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)


# Access Error: invalid token
def test_channel_details_invalid_token(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('onelast@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', True, CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_details('NOT_A_TOKEN', chnl['channel_id'], CHANNEL_DATA, USER_DATA)


'''
########## Tests for channel_messages bellow ##########
'''
# Correct case with no messages
def test_channel_messages_correct_nomessages(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Correct output if no messages added
    correct_output = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    result = channel_messages(usr1['token'], chnl['channel_id'], 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)
    
    # Check output
    assert result == correct_output


# Correct case with 2 messages
def test_channel_messages_correct_two_messages(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Add two messages and prepares expected output
    i = 0

    # Correct output
    correct_output = {
                'messages': [],
                'start': 0,
                'end': -1
                }
    while (i < 2):
        message_send(usr1['token'], chnl['channel_id'], f'this is message {i}', USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
        correct_output['messages'].insert(0, {
                                        'message_id': i,
                                        'u_id': usr1['u_id'],
                                        'message': f'this is message {i}',
                                        'time_created': int(time.time()),
                                        'reacts': 0,
                                        'is_pinned': 0
                                        })
        i = i + 1

    result = channel_messages(usr1['token'], chnl['channel_id'], 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)

    # Check output
    assert result == correct_output


# Correct case with 125 messages
def test_channel_messages_correct_125_messages(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Add 125 messages and prepares expected output
    i = 0

    # Correct output
    correct_output1 = {
                'messages': [],
                'start': 0,
                'end': 50
                }
    correct_output2 = {
                'messages': [],
                'start': 50,
                'end': 100
                }
    correct_output3 = {
                'messages': [],
                'start': 100,
                'end': -1
                }
    while (i < 125):
        message_send(usr1['token'], chnl['channel_id'], f'this is message {i}', USER_DATA, CHANNEL_DATA, MESSAGE_DATA)
        # Collects most recent 50
        if i > 74:
            correct_output1['messages'].insert(0,{
                                            'message_id': i,
                                            'u_id': usr1['u_id'],
                                            'message': f'this is message {i}',
                                            'time_created': int(time.time()),
                                            'reacts': 0,
                                            'is_pinned': 0
                                            })
        # Collects center 50
        elif i > 24:
            correct_output2['messages'].insert(0,{
                                            'message_id': i,
                                            'u_id': usr1['u_id'],
                                            'message': f'this is message {i}',
                                            'time_created': int(time.time()),
                                            'reacts': 0,
                                            'is_pinned': 0
                                            })
        # Collects last 25
        else:
            correct_output3['messages'].insert(0,{
                                            'message_id': i,
                                            'u_id': usr1['u_id'],
                                            'message': f'this is message {i}',
                                            'time_created': int(time.time()),
                                            'reacts': 0,
                                            'is_pinned': 0
                                            })
        i = i + 1

    # Check result
    result = channel_messages(usr1['token'], chnl['channel_id'], 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)
    assert result == correct_output1

    result = channel_messages(usr1['token'], chnl['channel_id'], 50, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)
    assert result == correct_output2

    result = channel_messages(usr1['token'], chnl['channel_id'], 100, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)
    assert result == correct_output3


# Input Error - Channel ID is not a valid channel
def test_channel_messages_input_error_channelID(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Check for Input Error 
    with pytest.raises(InputError) as e:
        channel_messages(usr1['token'], 100**100, 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)


# Input Error - Start is greater than the total number of messages
def test_channel_messages_input_error_messages(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Check for Input Error 
    with pytest.raises(InputError) as e:
        channel_messages(usr1['token'], chnl['channel_id'], 100**100, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)


# Access Error 
def test_channel_messages_access_error(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('twotwo@gmail.com', 'ThisisPW1234!', 'two', 'two', USER_DATA)

    # Check for Access Error when unauth_u_uid requests message to channel_id
    with pytest.raises(AccessError) as e:
        channel_messages(usr2['token'], chnl['channel_id'], 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA) 


# Access Error 
def test_channel_messages_invalid_token(user_data_init, channel_data_init, message_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init
    MESSAGE_DATA = message_data_init

    usr1 = auth_register('oneone@gmail.com', 'ThisisPW1234!', 'one', 'one', USER_DATA)
    chnl = channels_create(usr1['token'],'Ones channel', False, CHANNEL_DATA, USER_DATA)

    # Check for Access Error when invalid token is used
    with pytest.raises(AccessError) as e:
        channel_messages(100**100, chnl['channel_id'], 0, CHANNEL_DATA, MESSAGE_DATA, USER_DATA)      


'''
########## Tests for channel_leave bellow ##########
'''
# channel_leave test with no errors
def test_channel_leave_correct(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr['token'],'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    assert channel_leave(usr['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {}

    assert CHANNEL_DATA['channels'][0]['members'] == []


# Input Error: channel_id is not a valid channel 
def test_channel_leave_input_error(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr['token'],'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_leave(usr['token'], 100**100, CHANNEL_DATA, USER_DATA)


# Access Error: User is not a member of channel_id
def test_channel_leave_access_error(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)
    with pytest.raises(AccessError) as e:
        channel_leave(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)    


'''
########## Tests for channel_join bellow ##########
'''
# channel_join test with no errors, user not yet joined (public channel)
def test_channel_join_not_joined(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', True, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)

    assert channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {}
    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


# channel_join test with no errors, owner not yet joined (private channel)
def test_channel_join_owner_not_joined(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)
    chnl = channels_create(usr2['token'],'Miketwos channel', False, CHANNEL_DATA, USER_DATA)

    assert channel_join(usr1['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {}
    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr2['u_id'], 'rank': 1}, \
                                        {'u_id': usr1['u_id'], 'rank': 1}])


# channel_join test with no errors, user already joined
def test_channel_join_twice(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', True, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)

    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    assert channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA) == {}
    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


# Input Error: channel_id is not a valid channel 
def test_channel_join_input_error_joined(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', True, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)

    with pytest.raises(InputError) as e:
        channel_join(usr2['token'], 100**100, CHANNEL_DATA, USER_DATA)


# Access Error: channel_id refers to a channel that is private
def test_channel_join_access_error(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', False, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)    


# Access Error: invalid token
def test_channel_join_invalid_token(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('mikegysel0000@gmail.com', 'ThisisPW1234!', 'Mike', 'Gysel', USER_DATA)
    chnl = channels_create(usr1['token'],'Mikes channel', True, CHANNEL_DATA, USER_DATA)

    usr2 = auth_register('mikegysel2@gmail.com', 'ThisisPW1234!', 'Miketwo', 'Gyseltwo', USER_DATA)
    
    with pytest.raises(AccessError) as e:
        channel_join('NOT_A_TOKEN', chnl['channel_id'], CHANNEL_DATA, USER_DATA)


'''
########## Tests for channel_addowner bellow ##########
'''
#without an error
def test_channel_addowner(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])

    channel_addowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 1}])


#without an error
def test_channel_addowner_not_member(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}])

    channel_addowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 1}])


#input error when channel id isnt valid
def test_channel_addowner_invalid_channel(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)

    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)
    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_addowner(usr1['token'], 100**100, usr2['u_id'], CHANNEL_DATA, USER_DATA)


#input error when the user is already owner of channel
def test_channel_addowner_user_already_owner(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_addowner(usr1['token'], chnl['channel_id'], usr1['u_id'], CHANNEL_DATA, USER_DATA)


#access error when the user isnt the owner of the channel
def test_channel_addowner_user_not_owner(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    usr3 = auth_register('bill@uni.com.au', 'billsuniacc33', 'Bill', 'Person', USER_DATA)

    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)
    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)
    channel_join(usr3['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_addowner(usr2['token'], chnl['channel_id'], usr3['u_id'], CHANNEL_DATA, USER_DATA)


#access error when the token is invalid
def test_channel_addowner_invalid_token(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)

    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)
    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_addowner('NOT_A_TOKEN', chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)


'''
########## Tests for channel_removeowner bellow ##########
'''
#without an error
def test_channel_removeowner(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_addowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 1}])

    channel_removeowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


#without an error, self
def test_channel_removeowner_self(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_addowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    channel_removeowner(usr2['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    assert (CHANNEL_DATA['channels'][chnl['channel_id']]['members'] == \
                                        [{'u_id': usr1['u_id'], 'rank': 1}, \
                                        {'u_id': usr2['u_id'], 'rank': 0}])


#input error when channel id isnt valid
def test_channel_removeowner_invalid_channel(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_addowner(usr1['token'], chnl['channel_id'], usr2['u_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(InputError) as e:
        channel_removeowner(usr1['token'], 100**100, usr2['u_id'], CHANNEL_DATA, USER_DATA)


#access error when the user isnt the owner of the channel
def test_channel_removeowner_user_not_owner(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_removeowner(usr2['token'], chnl['channel_id'], usr1['u_id'], CHANNEL_DATA, USER_DATA)


#access error when the token is invalid
def test_channel_removeowner_invalid_token(user_data_init, channel_data_init):
    USER_DATA = user_data_init
    CHANNEL_DATA = channel_data_init

    usr1 = auth_register('jade@uni.com.au', 'Jadesuniacc33', 'Jade', 'Burger', USER_DATA)
    usr2 = auth_register('sally@uni.com.au', 'sallysuniacc33', 'Sally', 'Person', USER_DATA)
    chnl = channels_create(usr1['token'],'Jades channel', True, CHANNEL_DATA, USER_DATA)

    channel_join(usr2['token'], chnl['channel_id'], CHANNEL_DATA, USER_DATA)

    with pytest.raises(AccessError) as e:
        channel_removeowner('NOT_A_TOKEN', chnl['channel_id'], usr1['u_id'], CHANNEL_DATA, USER_DATA)
