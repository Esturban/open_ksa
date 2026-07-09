from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API key: {api_key[:10]}...{api_key[-4:]}")
print(f"API key length: {len(api_key) if api_key else 0}")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hi"}],
        max_completion_tokens=10
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error: {type(e).__name__}")
    print(f"Details: {str(e)[:500]}")

