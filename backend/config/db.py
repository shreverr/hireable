import mongoengine as me

from os import getenv

def connectDb():
    if getenv("MONGO_URI"):
        me.connect("hireable", host="mongodb://localhost:27017/hireable")
        print("Database connected successfully")
    else:
      raise ValueError("MONGO_URI not found")