from datetime import datetime

import pyotp
import qrcode

from .encryption import multi_fernet_instance

base32_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

# Since all keys are base32 or 64, the records are kept as strings to be transparent 
# about how the data is supposed to be represented in case another application may access the DB.

def get_plain_otp_key():
    """
    Returns a key for a OTP instance in plaintext. Should NEVER be exposed to a user.
    """
    return pyotp.random_base32()

def encrypt_otp_key(otp_key: str):
    return str(multi_fernet_instance.encrypt(bytes(otp_key, encoding='utf-8')), encoding='utf-8')
    
def decrypt_otp_key(otp_key: str):
    return str(multi_fernet_instance.decrypt(bytes(otp_key, encoding='utf-8')), encoding='utf-8')

def get_safe_otp_key():
    return encrypt_otp_key(get_plain_otp_key())

def get_cur_totp_for_key(key: str):
    return pyotp.TOTP(key, digits=8).now()

def get_totp_for_key_at(key: str, dt: datetime):
    return pyotp.TOTP(key, digits=8).at(dt)

def totp_for_key_is_valid(key: str, totp: str, dt: datetime | None = None):
    if dt is None:
        return totp == get_cur_totp_for_key(key)
    else:
        return totp == get_totp_for_key_at(key, dt)

def get_totp_instance(account_name: str, secret: str | None):
    if secret is None:
        secret == get_plain_otp_key()
    else:
        if len(secret) != 32:
            raise ValueError('Key for 2FA must be 32 characters long')
        if any((char not in base32_charset for char in secret)):
            raise ValueError('Invalid base32 for secret')
    return pyotp.TOTP(secret, digits=8, interval=30, issuer='SenDT', name=account_name)

def get_totp_uri(account_name: str, secret: str | None):
    totp = get_totp_instance(account_name, secret)
    
    return totp.provisioning_uri()
    
def get_totp_qr_code(account_name: str, secret: str | None):
    uri = get_totp_uri(account_name, secret)
    
    return qrcode.make(uri)
    
    