from dotenv import load_dotenv
load_dotenv()

from config.db import connectDb
connectDb()

from models.user import User
from web_scraper.scrape_socials import scrapeSocials

# print(scrapeSocials([], "68a5997d07ace7a363f02ae9"))

print("app running")