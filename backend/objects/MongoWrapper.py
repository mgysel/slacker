from pymongo import MongoClient
import json
import os

class CredentialsError(Exception):
    def __init__(self, message):
        self.message = message

class MongoWrapper:
    '''
    Wrapper class for ensuring one instance of MongoClient client, as per the Borg pattern.
    Credentials file is checked for valid properties.
    '''
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        try:
            username = os.environ.get('DATABASE_USERNAME')
            if username is None:
                raise CredentialsError("Username not set as environment variable")
            password = os.environ.get('DATABASE_PASSWORD')
            if password is None:
                raise CredentialsError("Password not set as environment variable")
            connection_string = f"mongodb+srv://<username>:<password>@cluster1.oc2krpz.mongodb.net/?retryWrites=true&w=majority".replace('<username>', username).replace('<password>', password)
            self.client = MongoClient(connection_string)
        except:
            raise CredentialsError("Credentials not valid")