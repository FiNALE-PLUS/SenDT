from datetime import datetime
from os import listdir
from re import compile as compile_regex
from secrets import randbelow

from cryptography.fernet import Fernet, MultiFernet

from const import BASE_DIR

FERNET_KEYS_DIR = BASE_DIR / 'private' / '2fa' / 'fernet'
FERNET_KEYS_DIR.mkdir(parents=True, exist_ok=True)

def generate_new_fernet_key():
    key = Fernet.generate_key()
    
    timestamp = int(datetime.now().timestamp())
    # Add a discriminator to the timestamp to prevent collisions
    filename = f'{timestamp}-{hex(randbelow(16<<16))[2:]:0>5}'
    with open(FERNET_KEYS_DIR / filename, 'wb') as f:
        f.write(key)


# Run on startup 
if len(listdir(FERNET_KEYS_DIR.absolute())) == 0:
    generate_new_fernet_key()
    
# set up a multi fernet to allow for future key rotations
fernet_instances = []
for key_path in (FERNET_KEYS_DIR / fname for fname in listdir(FERNET_KEYS_DIR)):
    if not key_path.is_file():
        continue
    
    with open(key_path, 'r') as key_file:
        key = key_file.read()
        assert len(key) == 44
        fernet_instances.append(Fernet(key=key))


multi_fernet_instance = MultiFernet(fernet_instances)
    