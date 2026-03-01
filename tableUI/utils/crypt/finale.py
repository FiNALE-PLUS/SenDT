# https://github.com/donmai-me/MaiConverter/blob/master/maiconverter/maicrypt/maifinalecrypt.py
import gzip
import os
from binascii import unhexlify
from typing import Union

from Crypto.Cipher import AES
from typing_extensions import deprecated

from environment_vars import CRYPT_KEY
from tableUI.utils.settings.get_settings import get_settings_default_crypt_key


def encrypt_finale_file(
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


def encrypt_file_with_default_settings_key(plaintext: bytes) -> bytes:
    key = get_settings_default_crypt_key()

    if key is None:
        raise ValueError("no default key provided")

    return encrypt_finale_file(key, plaintext)


@deprecated("Use default key from `settings.json` instead")
def encrypt_table_with_env_key(plaintext: bytes) -> bytes:
    return encrypt_finale_file(CRYPT_KEY, plaintext)
