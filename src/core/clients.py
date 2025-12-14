import os
from openai import OpenAI
from tzafon import Computer
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("TZAFON_API_KEY", "")

llm_client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.tzafon.ai/v1",
)

client = Computer(api_key=API_KEY)
