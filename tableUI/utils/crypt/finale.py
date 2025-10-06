# https://github.com/donmai-me/MaiConverter/blob/master/maiconverter/maicrypt/maifinalecrypt.py
import gzip
import os
from binascii import unhexlify
from typing import Union

from Crypto.Cipher import AES

from environment_vars import CRYPT_KEY


def encrypt_table(
    key: Union[str, bytes],
    plaintext: bytes,
) -> bytes:
    if not isinstance(key, bytes):
        key = int(key.replace(" ", ""), 0).to_bytes(0x10, "big")
    if len(key) != 0x10:
        raise ValueError("Invalid key length")

    JUNK = unhexlify("4b67ca1eebc78fb9964f781019bc4903")
    encoded = JUNK + plaintext

    gzipdata = gzip.compress(encoded)
    if len(gzipdata) % 0x10 != 0:
        amount = 0x10 - (len(gzipdata) % 0x10)
        padding = amount.to_bytes(1, "big") * amount
        gzipdata += padding

    iv = os.urandom(0x10)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return iv + cipher.encrypt(gzipdata)


def encrypt_table_with_env_key(plaintext: bytes) -> bytes:
    return encrypt_table(CRYPT_KEY, plaintext)