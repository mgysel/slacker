# Slackr

Slackr was built as part of UNSW's Software Engineering Fundamentals course and the hosted web application can be found [here](https://slackr-4fa3d8731f8d.herokuapp.com/login). Specifically, our group built the backend system per the specifications in the Overview section; since the course, I updated the web application to use a persistent database and hosted the project.

## Overview

Rather than re-invent the wheel, UNSW has decided that it finds the functionality of **<a href="https://slack.com/intl/en-au/">Slack</a>** to be nearly exactly what it needs. For this reason, UNSW has contracted out Lit Pty Ltd (a small software business run by Hayden) to build the new product. In UNSW's attempt to connect with the younger and more "hip" generation that fell in love with flickr, Tumblr, etc, they would like to call the new UNSW-based product **slackr**.

Beside the information available in the interface that Sally and Bob provided, you have been told (so far) that the features of slackr that UNSW would like to see implemented include:

1. Ability to login, register if not registered, and log out
2. Ability to reset password if forgotten it
3. Ability to see a list of channels
4. Ability to create a channel, join a channel, invite someone else to a channel, and leave a channel
5. Within a channel, ability to view all messages, view the members of the channel, and the details of the channel
6. Within a channel, ability to send a message now, or to send a message at a specified time in the future
7. Within a channel, ability to edit, remove, pin, unpin, react, or unreact to a message
8. Ability to view user anyone's user profile, and modify a user's own profile (name, email, handle, and profile photo)
9. Ability to search for messages based on a search string
10. Ability to modify a user's privileges: (MEMBER, OWNER)
11. Ability to begin a "standup", which is an X minute period where users can send messages that at the end of the period will automatically be collated and summarised to all users

## Interface specifications

### Data types

|Variable name|Type|
|-------------|----|
|named exactly **email**|string|
|named exactly **id**|integer|
|named exactly **length**|integer|
|named exactly **password**|string|
|named exactly **token**|string|
|named exactly **message**|string|
|contains substring **name**|string|
|contains substring **code**|string|
|has prefix **is_**|boolean|
|has prefix **time_**|integer (unix timestamp), [check this out](https://www.tutorialspoint.com/How-to-convert-Python-date-to-Unix-timestamp)|
|has suffix **_id**|integer|
|has suffix **_url**|string|
|has suffix **_str**|string|
|has suffix **end**|integer|
|has suffix **start**|integer|
|(outputs only) named exactly **user**|Dictionary containing u_id, email, name_first, name_last, handle_str, profile_img_url|
|(outputs only) named exactly **users**|List of dictionaries, where each dictionary contains types u_id, email, name_first, name_last, handle_str, profile_img_url|
|(outputs only) named exactly **messages**|List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_created, reacts, is_pinned  }|
|(outputs only) named exactly **channels**|List of dictionaries, where each dictionary contains types { channel_id, name }|
|(outputs only) name ends in **members**|List of dictionaries, where each dictionary contains types { u_id, name_first, name_last, profile_img_url }|
|(outputs only) name ends in **reacts**|List of dictionaries, where each dictionary contains types { react_id, u_ids, is_this_user_reacted } where react_id is the id of a react, and u_ids is a list of user id's of people who've reacted for that react. is_this_user_reacted is whether or not the authorised user has been one of the reacts to this post|


### profile_img_url & image uploads

For outputs with data pertaining to a user, a profile_img_url is present. When images are uploaded for a user profile, after processing them you should store them on the server such that your server now locally has a copy of the cropped image of the original file linked. Then, the profile_img_url should be a URL to the server, such as http://localhost:5001/imgurl/adfnajnerkn23k4234.jpg (a unique url you generate).

Note: This is most likely the most challenging part of the project. Don't get lost in this, we would strongly recommend most teams complete this capability *last*.

### Token

Many of these functions (nearly all of them) need to be called from the perspective of a user who is logged in already. When calling these "authorised" functions, we need to know:
1) Which user is calling it
2) That the person who claims they are that user, is actually that user

We could solve this trivially by storing the user ID of the logged in user on the front end, and every time the front end (from Sally and Bob) calls your background, they just sent a user ID. This solves our first problem (1), but doesn't solve our second problem! Because someone could just "hack" the front end and change their user id and then log themselves in as someone else.

To solve this when a user logs in or registers the backend should return a "token" (an authorisation hash) that the front end will store and pass into most of your functions in future. When these "authorised" functions are called, you can check if a token is valid, and determine the user ID.

### Error raising for the frontend

For errors to be appropriately raised on the frontend, they must be raised by the following:

```python
if True: # condition here
    raise InputError(description='Description of problem')
```

The types in error.py have been modified appropriately for you.

### Reacts

The only React ID currently associated with the frontend is React ID 1, which is a thumbs up. You are welcome to add more (this will require some frontend work)


### Permissions:
 * Members in a channel have one of two channel permissions.
   * 1) Owner of the channel (the person who created it, and whoever else that creator adds)
   * 2) Members of the channel
 * Slackr user's have two global permissions
   * 1) Owners, who can also modify other owners' permissions. (permission_id 1)
   * 2) Members, who do not have any special permissions. (permission_id 2)
 * All slackr users are by default members, except for the very first user who signs up, who is an owner

A user's primary permissions are their global permissions. Then the channel permissions are layered on top. For example:
* An owner of slackr has owner privileges in every channel they've joined
* A member of slackr is a member in channels they are not owners of
* A member of slackr is an owner in channels they are owners of

### Standups

Once standups are finished, all of the messages sent to standup/send are packaged together in *one single message* posted by *the user who started the standup* and sent as a message to the channel the standup was started in, timestamped at the moment the standup finished.

The structure of the packaged message is like this:

[message_sender1_handle]: [message1]

[message_sender2_handle]: [message2]

[message_sender3_handle]: [message3]

[message_sender4_handle]: [message4]

For example:

```txt
hayden: I ate a catfish
rob: I went to kmart
michelle: I ate a toaster
isaac: my catfish ate a toaster
```

Standups can be started on the frontend by typing "/standup X", where X is the number of seconds that the standup lasts for, into the message input and clicking send.

### Errors for all functions

**AccessError**
 * For all functions except auth/register, auth/login
 * Error thrown when token passed in is not a valid token

### Pagination
The behaviour in which channel_messages returns data is called **pagination**. It's a commonly used method when it comes to getting theoretially unbounded amounts of data from a server to display on a page in chunks. Most of the timelines you know and love - Facebook, Instagram, LinkedIn - do this.

For example, if we imagine a user with token "12345" is trying to read messages from channel with ID 6, and this channel has 124 messages in it, 3 calls from the client to the server would be made. These calls, and their corresponding return values would be:
 * channel_messages("12345", 6, 0) => { [messages], 0, 50 }
 * channel_messages("12345", 6, 50) => { [messages], 50, 100 }
 * channel_messages("12345", 6, 100) => { [messages], 100, -1 }

### Other Comments
* All IDs (e.g. user id, channel id) uniquely identify a data item for its entire existence. Even if that item is removed, the ID cannot be reused for any new or other existing items.

### Interface

|HTTP Route|HTTP Method|Parameters|Return type|Exceptions|Description|
|------------|-------------|-------------|----------|-----------|----------|
|auth/login|POST|(email, password)|{ u_id, token }|**InputError** when any of:<ul><li>Email entered is not a valid email using the method provided [here](https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/) (unless you feel you have a better method)</li><li>Email entered does not belong to a user</li><li>Password is not correct</li></ul> | Given a registered users' email and password and generates a valid token for the user to remain authenticated |
|auth/logout|POST|(token)|{ is_success }|N/A|Given an active token, invalidates the taken to log the user out. If a valid token is given, and the user is successfully logged out, it returns true, otherwise false. |
|auth/register|POST|(email, password, name_first, name_last)|{ u_id, token }|**InputError** when any of:<ul><li>Email entered is not a valid email using the method provided [here](https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/) (unless you feel you have a better method).</li><li>Email address is already being used by another user</li><li>Password entered is less than 6 characters long</li><li>name_first not is between 1 and 50 characters inclusive in length</li><li>name_last is not between 1 and 50 characters inclusive in length</ul>|Given a user's first and last name, email address, and password, create a new account for them and return a new token for authentication in their session. A handle is generated that is the concatentation of a lowercase-only first name and last name. If the concatenation is longer than 20 characters, it is cutoff at 20 characters. If the handle is already taken, you may modify the handle in any way you see fit to make it unique. |
|auth/passwordreset/request|POST|(email)|{}|N/A|Given an email address, if the user is a registered user, send's them a an email containing a specific secret code, that when entered in auth_passwordreset_reset, shows that the user trying to reset the password is the one who got sent this email.|
|auth/passwordreset/reset|POST|(reset_code, new_password)|{}|**InputError** when any of:<ul><li>reset_code is not a valid reset code</li><li>Password entered is not a valid password</li>|Given a reset code for a user, set that user's new password to the password provided|
|channel/invite|POST|(token, channel_id, u_id)|{}|**InputError** when any of:<ul><li>channel_id does not refer to a valid channel that the authorised user is part of.</li><li>u_id does not refer to a valid user</li></ul>**AccessError** when<ul><li>the authorised user is not already a member of the channel</li>|Invites a user (with user id u_id) to join a channel with ID channel_id. Once invited the user is added to the channel immediately|
|channel/details|GET|(token, channel_id)|{ name, owner_members, all_members }|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li></ul>**AccessError** when<ul><li>Authorised user is not a member of channel with channel_id</li></ul>|Given a Channel with ID channel_id that the authorised user is part of, provide basic details about the channel|
|channel/messages|GET|(token, channel_id, start)|{ messages, start, end }|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>start is greater than the total number of messages in the channel</li></ul>**AccessError** when<ul><li>Authorised user is not a member of channel with channel_id</li></ul>|Given a Channel with ID channel_id that the authorised user is part of, return up to 50 messages between index "start" and "start + 50" exclusive. Message with index 0 is the most recent message in the channel. This function returns a new index "end" which is the value of "start + 50", or, if this function has returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to load after this return.|
|channel/leave|POST|(token, channel_id)|{}|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li></ul>**AccessError** when<ul><li>Authorised user is not a member of channel with channel_id</li></ul>|Given a channel ID, the user removed as a member of this channel|
|channel/join|POST|(token, channel_id)|{}|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li></ul>**AccessError** when<ul><li>channel_id refers to a channel that is private (when the authorised user is not an owner)</li></ul>|Given a channel_id of a channel that the authorised user can join, adds them to that channel|
|channel/addowner|POST|(token, channel_id, u_id)|{}|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>When user with user id u_id is already an owner of the channel</li></ul>**AccessError** when the authorised user is not an owner of the slackr, or an owner of this channel</li></ul>|Make user with user id u_id an owner of this channel|
|channel/removeowner|POST|(token, channel_id, u_id)|{}|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>When user with user id u_id is not an owner of the channel</li></ul>**AccessError** when the authorised user is not an owner of the slackr, or an owner of this channel</li></ul>|Remove user with user id u_id an owner of this channel|
|channels/list|GET|(token)|{ channels }|N/A|Provide a list of all channels (and their associated details) that the authorised user is part of|
|channels/listall|GET|(token)|{ channels }|N/A|Provide a list of all channels (and their associated details)|
|channels/create|POST|(token, name, is_public)|{ channel_id }|**InputError** when any of:<ul><li>Name is more than 20 characters long</li></ul>|Creates a new channel with that name that is either a public or private channel|
|message/send|POST|(token, channel_id, message)|{ message_id }|**InputError** when any of:<ul><li>Message is more than 1000 characters</li></ul>**AccessError** when: <li> the authorised user has not joined the channel they are trying to post to</li></ul>|Send a message from authorised_user to the channel specified by channel_id|
|message/sendlater|POST|(token, channel_id, message, time_sent)|{ message_id }|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>Message is more than 1000 characters</li><li>Time sent is a time in the past</li></ul>**AccessError** when: <li> the authorised user has not joined the channel they are trying to post to</li></ul>|Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future|
|message/react|POST|(token, message_id, react_id)|{}|**InputError** when any of:<ul><li>message_id is not a valid message within a channel that the authorised user has joined</li><li>react_id is not a valid React ID. The only valid react ID the frontend has is 1</li><li>Message with ID message_id already contains an active React with ID react_id from the authorised user</li></ul>|Given a message within a channel the authorised user is part of, add a "react" to that particular message|
|message/unreact|POST|(token, message_id, react_id)|{}|**InputError** 	<ul><li>message_id is not a valid message within a channel that the authorised user has joined</li><li>react_id is not a valid React ID</li><li>Message with ID message_id does not contain an active React with ID react_id</li></ul>|Given a message within a channel the authorised user is part of, remove a "react" to that particular message|
|message/pin|POST|(token, message_id)|{}|**InputError** when any of:<ul><li>message_id is not a valid message</li><li>Message with ID message_id is already pinned</li></ul>**AccessError** when any of:<ul><li>The authorised user is not a member of the channel that the message is within</li><li>The authorised user is not an owner</li></ul>|Given a message within a channel, mark it as "pinned" to be given special display treatment by the frontend|
|message/unpin|POST|(token, message_id)|{}|**InputError** when any of:<ul><li>message_id is not a valid message</li><li>Message with ID message_id is already unpinned</li></ul>**AccessError** when any of:<ul><li>The authorised user is not a member of the channel that the message is within</li><li>The authorised user is not an owner</li></ul>|Given a message within a channel, remove it's mark as unpinned|
|message/remove|DELETE|(token, message_id)|{}|**InputError** when any of:<ul><li>Message (based on ID) no longer exists</li></ul>**AccessError** when none of the following are true:<ul><li>Message with message_id was sent by the authorised user making this request</li><li>The authorised user is an owner of this channel or the slackr</li></ul>|Given a message_id for a message, this message is removed from the channel|
|message/edit|PUT|(token, message_id, message)|{}|**AccessError** when none of the following are true:<ul><li>Message with message_id was sent by the authorised user making this request</li><li>The authorised user is an owner of this channel or the slackr</li></ul>|Given a message, update it's text with new text. If the new message is an empty string, the message is deleted.|
|user/profile|GET|(token, u_id)|{ user }|**InputError** when any of:<ul><li>User with u_id is not a valid user</li></ul>|For a valid user, returns information about their user id, email, first name, last name, handle, and image profile URL.|
|user/profile/setname|PUT|(token, name_first, name_last)|{}|**InputError** when any of:<ul><li>name_first is not between 1 and 50 characters inclusive in length</li><li>name_last is not between 1 and 50 characters inclusive in length</ul></ul>|Update the authorised user's first and last name|
|/user/profile/setemail|PUT|(token, email)|{}|**InputError** when any of:<ul><li>Email entered is not a valid email using the method provided [here](https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/) (unless you feel you have a better method).</li><li>Email address is already being used by another user</li>|Update the authorised user's email address|
|/user/profile/sethandle|PUT|(token, handle_str)|{}|**InputError** when any of:<ul><li>handle_str must be between 2 and 20 characters inclusive</li><li>handle is already used by another user</li></ul>|Update the authorised user's handle (i.e. display name)|
|/user/profile/uploadphoto|POST|(token, img_url, x_start, y_start, x_end, y_end)|{}|**InputError** when any of:<ul><li>img_url returns an HTTP status other than 200.</li><li>any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.</li><li>Image uploaded is not a JPG</li></ul>|Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.|
|users/all|GET|(token)|{ users}|N/A|Returns a list of all users and their associated details|
|/search|GET|(token, query_str)|{ messages }|N/A|Given a query string, return a collection of messages in all of the channels that the user has joined that match the query. Results are sorted from most recent message to least recent message|
|standup/start|POST|(token, channel_id, length)|{ time_finish }|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>An active standup is currently running in this channel</li></ul>|For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup_send" with a message, it is buffered during the X second window then at the end of the X second window a message will be added to the message queue in the channel from the user who started the standup. X is an integer that denotes the number of seconds that the standup occurs for|
|standup/active|GET|(token, channel_id)|{ is_active, time_finish }|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li></ul>|For a given channel, return whether a standup is active in it, and what time the standup finishes. If no standup is active, then time_finish returns None|
|standup/send|POST|(token, channel_id, message)|{}|**InputError** when any of:<ul><li>Channel ID is not a valid channel</li><li>Message is more than 1000 characters</li><li>An active standup is not currently running in this channel</li></ul>**AccessError** when<ul><li>The authorised user is not a member of the channel that the message is within</li></ul>|Sending a message to get buffered in the standup queue, assuming a standup is currently active|
|admin/userpermission/change|POST|(token, u_id, permission_id)|{}|**InputError** when any of:<ul><li>u_id does not refer to a valid user<li>permission_id does not refer to a value permission</li></ul>**AccessError** when<ul><li>The authorised user is not an owner</li></ul>|Given a User by their user ID, set their permissions to new permissions described by permission_id|
|admin/user/remove|DELETE|(token, u_id)|{}|**InputError** when:<ul><li>u_id does not refer to a valid user</li></ul>**AccessError** when<ul><li>The authorised user is not an owner of the slackr</li></ul>|Given a User by their user ID, remove the user from the slackr. |
|workspace/reset|POST|()|{}||Resets the workspace state|
