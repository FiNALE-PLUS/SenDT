from const import BASE_DIR

ALGORITHM = "EdDSA"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

with open(BASE_DIR / 'private' / 'private.pem', 'r') as priv_key_file:
    private_key = priv_key_file.read()
with open(BASE_DIR / 'private' / 'public.pem', 'r') as pub_key_file:
    public_key = pub_key_file.read()
