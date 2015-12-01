import os
from peewee import *

# Database for storing library info.
# This should be all the utility functions.

'''
# fields we're gonna need to track

file_GUID       // sha1? auto_increment id?
full_path_filename  // string
artist          // string
title           // string
duration_sec    // in fractional seconds (float)
last_played     // time; epoch timestamp?
category        // what type of file is this?
                //   bump / psa / promo / feedback / si / content
??????
'''



database = SqliteDatabase(None, threadlocals=False)

class BaseModel(Model):
    class Meta:
        database = database

class AudioFile(BaseModel):
    #file_hash = CharField() # probably don't need this; would change on metadata update
    filename = CharField()
    artist = CharField()
    title = CharField()
    duration = FloatField()
    last_played = DateTimeField()
    category = CharField()
    
    class Meta:
        db_table = 'audio'

class OverlordDB(object):
    def __init__(self, path, **connect_args):
        if path == None:
            path = os.path.dirname(__file__)
        self.dbname = os.path.join(path, 'overlord.db')
        self.connect_args = connect_args
    def __enter__(self):
        database.init(self.dbname, **self.connect_args)
    # setup tables if they don't exist
        database.create_tables([AudioFile], safe=True)
        database.connect()
        return database
    def __exit__(self, t, v, tb):
        database.close()
