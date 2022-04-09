import os
import random

from config import database_file, memes_folder
from peewee import *

db = SqliteDatabase(database_file)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    vkid = IntegerField(unique=True)


class Meme(BaseModel):
    filename = CharField()
    rating = IntegerField(default=0)


class Mark(BaseModel):
    user = ForeignKeyField(User, backref='marks')
    meme = ForeignKeyField(Meme, backref='marks')
    is_like = BooleanField(default=True)

    class Meta:
        indexes = (
            (('user', 'meme'), True),  # Note the trailing comma!
        )


db.connect()
db.create_tables([User, Meme, Mark])

for i in os.listdir(memes_folder):
    if not Meme.select().where(Meme.filename == i).exists():
        m = Meme(filename=i)
        m.save()


def get_new_meme(vkid) -> (Meme, None):
    u = User.select().where(User.vkid == vkid).get()
    memes = {i for i in Meme.select()}
    already_voted_memes = {i.meme for i in Mark.select().where(Mark.user == u)}
    new_memes = list(memes - already_voted_memes)
    if new_memes:
        return random.choice(new_memes)
    return None


