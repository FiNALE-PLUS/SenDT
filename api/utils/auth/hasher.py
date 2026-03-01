from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hasher = PasswordHash((
    Argon2Hasher(),
))


def verify_password(plain_password, hashed_password):
    return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hasher.hash(password)
