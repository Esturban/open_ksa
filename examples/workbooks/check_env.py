from dotenv import load_dotenv
import os

load_dotenv()

print("=== Environment Variables ===")
env_vars = [
    "OPENAI_API_KEY",
    "OR_API_KEY", 
    "OPENAI_BASE_URL",
    "BASE_URL",
    "OR_MODEL",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy"
]

for var in env_vars:
    val = os.getenv(var)
    if val:
        if "KEY" in var or "key" in var:
            print(f"{var}: {val[:10]}...{val[-4:]}")
        else:
            print(f"{var}: {val}")
    else:
        print(f"{var}: (not set)")

