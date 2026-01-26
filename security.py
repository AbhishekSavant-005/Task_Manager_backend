from fastapi import HTTPException, Header
from typing import Annotated
import os
from dotenv import load_dotenv
import ast

# Load environment variables from .env file
load_dotenv()

# Fetch API keys dictionary from .env and parse it
VALID_API_KEYS_STR = os.getenv("VALID_API_KEYS", "{}").strip()

# Parse the string representation of the dictionary
try:
    VALID_API_KEYS = ast.literal_eval(VALID_API_KEYS_STR)
except (ValueError, SyntaxError):
    VALID_API_KEYS = {}

def get_api_key(x_api_key: Annotated[str | None, Header()])-> dict:
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="x_api_key cannot be None or empty. Please provide a value"
        )
    
    # Validate API key against the ones in .env
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return {"status": "authenticated", "key_info": VALID_API_KEYS[x_api_key]}