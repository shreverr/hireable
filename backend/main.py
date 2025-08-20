from web_scraper.scrape_socials import scrapeSocials
from models.user import User
from config.db import connectDb
from dotenv import load_dotenv
load_dotenv()

connectDb()


print(scrapeSocials())
print("app running")
