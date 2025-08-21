from web_scraper.scrape_socials import scrapeSocials
from models.user import User
from config.db import connectDb
from dotenv import load_dotenv
load_dotenv()

connectDb()

# Example usage with only some optional fields provided
scrapeSocials(
  userId="demo-user-id",
  data={
    # "resume_url": "https://res.cloudinary.com/dpf6c8boe/image/upload/v1755758537/ShreshthResume23-7-25_uijy4w.pdf",
    "portfolio_url": "https://vinayaksarawagi.com/",  # optional
    # "githubUrl": "https://github.com/johndoe",  # optional
    # "linkedInUrl": "https://www.linkedin.com/in/johndoe/",  # optional
    # "leetcodeUrl": "https://leetcode.com/u/johndoe/",  # optional
    # "xUrl": "https://x.com/johndoe",  # optional
  },
)

print("app running")
