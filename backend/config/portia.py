import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMProvider,
)

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

config = Config.from_default(llm_provider=LLMProvider.GOOGLE,
                             default_model="google/gemini-2.5-flash",
                             google_api_key=GOOGLE_API_KEY)
