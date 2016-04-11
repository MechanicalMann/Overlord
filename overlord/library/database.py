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
    file_hash = CharField() # used to detect metadata updates
    file_mtime = DateTimeField() # also used in update detection
    filename = CharField(primary_key = True) 
    # let's make this the primary key, until we decide we need an autoincrementing index column of ints
    # Note: we will need to make the first .save() call with parameters .save(force_insert=True)
        # see http://docs.peewee-orm.com/en/latest/peewee/models.html#id3 for more info
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
