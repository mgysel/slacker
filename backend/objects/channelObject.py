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


class Channel:
    '''
    Channel class that contains basic channel info/methods
    '''
    def __init__(self, _id, channel_id, name, is_public, num_members, members, standup):
        self._id = _id
        self.channel_id = channel_id
        self.name = name
        self.is_public = is_public
        self.num_members = num_members
        self.members = members
        self.standup = standup

    @staticmethod
    def from_json(channel_json):
        '''
        Channel json object to Channel Object
        '''
        if channel_json != None:
            properties = ['channel_id', 'name', 'is_public', 'num_members', 'members', 'standup']
            for prop in properties:
                if prop not in channel_json:
                    return None
            _id = None
            if '_id' in channel_json:
                _id = channel_json['_id']
            return Channel(_id, channel_json['channel_id'], channel_json['name'], channel_json['is_public'], channel_json['num_members'], channel_json['members'], channel_json['standup'])

    def to_json(self):
        '''
        Channel object to json object
        NOTE: converts ObjectId to string
        '''
        obj = self.__dict__
        if obj['_id'] == None:
            del obj['_id']
        else:
            obj['_id'] = str(obj['_id'])
        return obj

    def get_all_channels():
        '''
        Returns list of Channel objects from the database
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['channels']
        return coll.find()

    @staticmethod
    def insert_one(channel):
        '''
        Inserts a channel object into the database
        '''
        json_obj = channel.to_json()
        print("JSON OBJ: ", json_obj)
        if json_obj != None:
            db = MongoWrapper().client['Peerstr']
            coll = db['channels']
            # Get channel id 
            try:
                channel_id = coll.count()
                json_obj['channel_id'] = channel_id + 1
                inserted = coll.insert_one(json_obj)
                return inserted.inserted_id
            except:
                return None

    @classmethod
    def find_channel_by_attribute(cls, attribute, channel_attribute):
        '''
        Finds a channel by a specific attribute
        Returns channel object
        '''
        db = MongoWrapper().client['Peerstr']
        coll = db['channels']
        channel_json = coll.find_one({ attribute: channel_attribute })

        return channel_json

    @classmethod
    def update_channel_attribute(cls, query_attribute, query_channel_attribute, attribute, channel_attribute):
        '''
        Queries for channel by query_attribute = query_channel_attribute
        Updates attribute of channel to channel_attribute
        '''
        query = { query_attribute: query_channel_attribute }
        values = { "$set": { attribute: channel_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['channels']
        coll.update_one(query, values)

    @classmethod
    def push_channel_attribute(cls, query_attribute, query_channel_attribute, attribute, channel_attribute):
        '''
        Queries for channel by query_attribute = query_channel_attribute
        Appends attribute of channel to channel_attribute
        '''
        query = { query_attribute: query_channel_attribute }
        values = { "$push": { attribute: channel_attribute } }
        db = MongoWrapper().client['Peerstr']
        coll = db['channels']
        coll.update_one(query, values)