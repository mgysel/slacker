# assumptions.md

Assumption work to go in this file in root directory


# auth.py:

1. Tokens, email, password, firstname and lastname are all strings
2. u_id is a integer
3. Tokens will be unique with each session
4. u_id will be constant throughout the users existance
5. The python value None, negative numbers and non-integers are not used as u_id's
6. Email addresses other than UNSW provided email addresses can be used to register
7. First and last names can be anywhere between 1 and 50 (inclusive)
8. InputError if no data is entered
9. In the first register test it is assumed no users have been made and the test will make the first
10. For login and logout tests it is assumed that the regester function within auth.py is functional
11. If a invalid token is given to logout function in auth.py an AccessError occurs
12. When you register you are immediately logged-in
13. 'NotAToken' is not a token


# user.py:

1. auth.py and all its functions and working as required without any errors
2. user_profile can be used by a user on themselves
3. Users handle is passed as a string
4. Tests for user_profile_sethandle assume user_profile can be used
5. Handle must be between 3 and 20 characters (inclusive)
6. 'NotAToken' is not a token
7. First and last names must be between 1 and 50 characters in length
8. user_profile accurately reflects changes in the users name and email 
9. If we register a user using a specific email, that email is now in use (cannot be updated for use by another user)
10. An "is_email" type function is correctly implemented which identifies that "help.com" is not a valid email


# channels.py and channel.py:

1. when user makes channel, theyre automatically the owner
2. can have multiple channels with the same name 
3. there is no limit into how many channels a user can have
4. channel id's will be numbers
5. all users will get tokens
6. always avalibale to make more users
7. u_id will always be a number, starting at 1 and increasing by 1 with each user
8. adding an owner will never be rejected
9. wont reject if user isnt in any channels to begin with 
10. If no messages added in channel_messages, messages key is an empty array
11. When testing for channel_messages, the timestamp for the message created is within 1,000 seconds of the timestamp created by the test
12. Channels in channels_listall are listed in the order of when they were created.


# message.py:

1. auth.py and all its functions and working as required without any errors
2. channels_create() is implemented correctly
3. (x * 1001) is a string containing more than 1k characters 
4. 9999999999 is an invalid channel_id
5. A channel cannot exist if it has not been created
6. A user who has not been invited to or joined a non public channel does not have authorisation to send messages to that channel
7. If you succesfully remove a message once, then that message cannot be removed again 
8. Someone who has not sent a message or who is not the owner/ admin of a channel cannot remove a message 
9. The message_edit function calls message_remove if new message is an empty string


# other.py: 

1. The search function should find a message that has successfully been sent to a channel by an authorised user
2. If no messages have been sent the search function should return no messages 
3. The timer will start and users with a different timezone will recieve the message at the designated time the user specified
4. User alls means not including users that have made an account but deleted it
5. Can change a users permissions without their approval 
6. When a user is deleted, their messages with their user name will still be visable but unable to access user from message
7. Stand ups will always be availiable to use 
8. Message order will be determined when the message is delievered (regardless of the time its sent)
