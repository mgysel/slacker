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


class Message:
    '''
    Message class that contains basic user info/methods
    '''
    def __init__(self, _id, message_id, u_id, channel_id, message, time_created, reacts, is_pinned):
        self._id = _id
        self.message_id = message_id
        self.u_id = u_id
        self.channel_id = channel_id
        self.message = message
        self.time_created = time_created
        self.reacts = reacts
        self.is_pinned = is_pinned

    @staticmethod
    def from_json(msg_json):
        '''
        Message json object to Message Object
        '''
        if msg_json != None:
            properties = ['message_id', 'u_id', 'message', 'time_created', 'reacts', 'is_pinned']
            for prop in properties:
                if prop not in msg_json:
                    return None
            _id = None
            if '_id' in msg_json:
                _id = msg_json['_id']
            return Message(_id, msg_json['message_id'], msg_json['u_id'], msg_json['message'], msg_json['time_created'], msg_json['reacts'], msg_json['is_pinned'])

    def to_json(self):
        '''
        Message object to json object
        NOTE: converts ObjectId to string
        '''
        obj = self.__dict__
        if obj['_id'] == None:
            del obj['_id']
        else:
            obj['_id'] = str(obj['_id'])
        return obj

    def get_all_messages():
        '''
        Returns list of Message objects from the database
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']
        return coll.find()

    @staticmethod
    def insert_one(message):
        '''
        Inserts a message object into the database
        '''
        json_obj = message.to_json()
        if json_obj != None:
            db = MongoWrapper().client['Peerstr']
            coll = db['messages']
            # Get message id 
            try:
                message_id = coll.count() + 1
                json_obj['message_id'] = message_id
                inserted = coll.insert_one(json_obj)
                return inserted.inserted_id
            except:
                return None

    @classmethod
    def find_message_by_attribute(cls, attribute, msg_attribute):
        '''
        Finds a message by a specific attribute
        Returns message object
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']
        msg_json = coll.find_one({ attribute: msg_attribute })

        return msg_json
    
    @classmethod
    def find_messages_by_attribute(cls, attribute, msg_attribute):
        '''
        Finds a message by a specific attribute
        Returns message object
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']

        msgs_json = []
        for msg in coll.find({ attribute: msg_attribute }):
            msgs_json.append(msg)

        return msgs_json

    @classmethod
    def update_message_attribute(cls, query_attribute, query_msg_attribute, attribute, msg_attribute):
        '''
        Queries for message by query_attribute = query_message_attribute
        Updates attribute of message to message_attribute
        '''
        query = { query_attribute: query_msg_attribute }
        values = { "$set": { attribute: msg_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']
        coll.update_one(query, values)

    @classmethod
    def delete_message_by_attribute(cls, attribute, msg_attribute):
        '''
        Finds a message by a specific attribute
        Deletes message
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']
        msg_json = coll.delete_one({ attribute: msg_attribute })

        return msg_json

    @classmethod
    def push_message_attribute(cls, query_attribute, query_msg_attribute, attribute, msg_attribute):
        '''
        Queries for message by query_attribute = query_message_attribute
        Appends attribute of message to message_attribute
        '''
        query = { query_attribute: query_msg_attribute }
        values = { "$push": { attribute: msg_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['messages']
        coll.update_one(query, values)