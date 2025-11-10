import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    PERPLEXITY_BASE_URL = os.getenv("PERPLEXITY_BASE_URL")
    SCREENSHOT_DIR = "screenshots"
    WAIT_TIME = 2
    WAIT_TIME_GEMINI = 5
    SIMILARITY_THRESHOLD = 0.1
    CLICK_TYPE_TIMEOUT = 5000
