import os

from dotenv import load_dotenv

load_dotenv()

CRYPT_KEY = bytes.fromhex(os.getenv("CRYPT_KEY"))
