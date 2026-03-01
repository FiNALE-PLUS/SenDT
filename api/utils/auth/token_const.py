ALGORITHM = "EdDSA"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

with open('./private/private.pem', 'r') as priv_key_file:
    private_key = priv_key_file.read()
with open('./private/public.pem', 'r') as pub_key_file:
    public_key = pub_key_file.read()
