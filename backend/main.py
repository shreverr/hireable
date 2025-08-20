from dotenv import load_dotenv
load_dotenv()

from config.db import connectDb
connectDb()

from models.user import User

print("app running")