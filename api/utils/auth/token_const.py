from datetime import timedelta

from const import BASE_DIR

ALGORITHM = "EdDSA"
ACCESS_TOKEN_EXPIRE_HOURS = 24
TWO_FACTOR_TOKEN_EXPIRE_MINUTES = 5
TOKEN_EXPIRY_TIMEDELTA = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
TWO_FACTOR_TOKEN_EXPIRY_TIMEDELTA = timedelta(minutes=TWO_FACTOR_TOKEN_EXPIRE_MINUTES)

with open(BASE_DIR / 'private' / 'private.pem', 'r') as priv_key_file:
    private_key = priv_key_file.read()
with open(BASE_DIR / 'private' / 'public.pem', 'r') as pub_key_file:
    public_key = pub_key_file.read()
