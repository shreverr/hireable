import mongoengine as me

from os import getenv

def connectDb():
    if getenv("MONGO_URI"):
        me.connect("hireable", host = getenv("MONGO_URI"))
        print("Database connected successfully")
    else:
      raise ValueError("MONGO_URI not found")