import pymongo

# If we use the Flask Configuration
'''
import sys
sys.path
sys.path.append(".")
sys.path.append("..")
sys.path.append("./flask-app")
#from server import mongo
'''

from werkzeug.security import generate_password_hash
from objects.MongoWrapper import MongoWrapper
from bson import ObjectId
import re


class User:
    '''
    User class that contains basic user info/methods
    '''
    def __init__(self, _id, u_id, email, password, name_first, name_last, handle_str, profile_img_url, token, reset_code, permission_id):
        self._id = _id
        self.u_id = u_id
        self.email = email
        self.password = password
        self.name_first = name_first
        self.name_last = name_last
        self.handle_str = handle_str
        self.token = token
        self.profile_img_url = profile_img_url
        self.reset_code = reset_code
        self.permission_id = permission_id

    @staticmethod
    def from_json(user_json):
        '''
        User json object to User Object
        '''
        if user_json != None:
            properties = ['u_id', 'email', 'password', 'name_first', 'name_last', 'handle_str', 'profile_img_url', 'token', 'reset_code', 'permission_id']
            for prop in properties:
                if prop not in user_json:
                    return None
            _id = None
            if '_id' in user_json:
                _id = user_json['_id']
            return User(_id, user_json['u_id'], user_json['email'], user_json['password'], user_json['name_first'], user_json['name_last'], user_json['handle_str'], user_json['profile_img_url'], user_json['token'], user_json['reset_code'], user_json['permission_id'])

    def to_json(self):
        '''
        User object to json object
        NOTE: converts ObjectId to string
        '''
        obj = self.__dict__
        if obj['_id'] == None:
            del obj['_id']
        else:
            obj['_id'] = str(obj['_id'])
        return obj

    def get_all_users():
        '''
        Returns list of User objects from the database
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        users = []
        for user_json in coll.find():
            user = User.from_json(user_json)
            users.append(user)
        return users

    @staticmethod
    def insert_one(user):
        '''
        Inserts a user object into the database
        '''
        json_obj = user.to_json()
        if json_obj != None:
            db = MongoWrapper().client['Peerstr']
            coll = db['users']
            # Get total number of items, update u_id
            try:
                total = coll.count()
                json_obj['u_id'] = total + 1
                largest_user_id = coll.find().sort([("u_id",pymongo.ASCENDING)]).limit(1)
                user_id = largest_user_id.next()['u_id'] + 1
                json_obj['u_id'] = user_id
            except:
                return None
            # Insert into database
            try:
                inserted = coll.insert_one(json_obj)
                return inserted.inserted_id
            except:
                return None

    @classmethod
    def find_user_by_attribute(cls, attribute, user_attribute):
        '''
        Finds a user by a specific attribute
        Returns user object
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        user_json = coll.find_one({ attribute: user_attribute })

        return user_json

    @classmethod
    def find_users_from_search(cls, query, page):
        """
        Returns users with matching name
        """
        PAGE_SIZE = 10
        filter = {
            '$or':
                [
                    {'first_name': {'$regex': f".*{query}.*", '$options': 'i'}},
                    {'last_name': {'$regex': f".*{query}.*", '$options': 'i'}},
                    {'email': {'$regex': f".*{query}.*", '$options': 'i'}}
                ]
        }
        skip = (int(page)-1)*PAGE_SIZE
        limit = PAGE_SIZE

        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        results = coll.find(filter=filter,skip=skip,limit=limit).collation({'locale':'en'}).sort([('email',1),('first_name',1),('last_name',1)])

        return [User.from_json(x) for x in results]

    @classmethod
    def update_user_attribute(cls, query_attribute, query_user_attribute, attribute, user_attribute):
        '''
        Queries for user by query_attribute = query_user_attribute
        Updates attribute of user to user_attribute
        '''
        query = { query_attribute: query_user_attribute }
        values = { "$set": { attribute: user_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        coll.update_one(query, values)

    @classmethod
    def update_user_attributes(cls, query_attribute, query_user_attribute, user_attributes):
        '''
        Queries for user by query_attribute = query_user_attribute
        Updates attribute of user to user_attribute
        '''
        query = { query_attribute: query_user_attribute }
        values = { "$set": { user_attributes } }
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        coll.update_one(query, values)

    @classmethod
    def push_user_attribute(cls, query_attribute, query_user_attribute, attribute, user_attribute):
        '''
        Queries for user by query_attribute = query_user_attribute
        Appends attribute of user to user_attribute
        '''
        query = { query_attribute: query_user_attribute }
        values = { "$push": { attribute: user_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        coll.update_one(query, values)

    @classmethod
    def update_user_attributes(cls, query_attribute, query_user_attribute, values):
        '''
        Queries for user by query_attribute = query_user_attribute
        Updates attribute of user to user_attribute
        '''
        query = { query_attribute: query_user_attribute }
        values = { "$set": values }
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        coll.update_one(query, values)

    @classmethod
    def num_users(cls):
        db = MongoWrapper().client['Peerstr']
        coll = db['users']
        # Get total number of items, update u_id
        try:
            total = coll.count()
            return total
        except:
            return 0

    ########## Checking user validity ##########
    @classmethod
    def valid_email(cls, email):
        '''
        Checks that email is valid - per regex below
        Checks that email is not None. 
        Original code from:
        https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
        '''
        regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

        # Compares email to regex format
        if email is not None and re.search(regex, email):
            return True

        return False
    
    @classmethod
    def valid_password(cls, password):
        '''
        Checks that password is valid - > 6 characters
        Checks that password is not None
        '''
        if password is not None and len(password) > 6:
            return True

        return False

    @classmethod
    def valid_matching_passwords(cls, password, confirm_password):
        '''
        Checks that passwords match
        Checks that confirm password is not None
        '''
        return confirm_password is not None and password == confirm_password
    
    @classmethod
    def valid_name(cls, name):
        '''
        Checks that name is valid - between 1 and 50 characteds
        Checks that name is not None. 
        Original code from:
        https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
        '''
        if name is not None and len(name) >= 1 and len(name) <= 50:
            return True

        return False

    @classmethod
    def is_valid_user(cls, user):
        '''
        Determines if user object is valid
        Returns True if valid, False otherwise
        '''
        attributes = ['_id', 'u_id', 'email', 'password', 'first_name', 'last_name', 'payment_methods', 'shipping_address', 'spotify_id', 'cart', 'role', 'reset_code']
        for attribute in attributes:
            if not hasattr(user, attribute):
                return False
        return True

    @classmethod
    def is_valid_id(cls, _id):
        '''
        Determines if _id is 24-character hex string
        '''
        return len(_id) == 24