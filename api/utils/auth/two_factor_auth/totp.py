import pyotp
import qrcode

base32_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

def get_otp_key():
    return pyotp.random_base32()

def get_cur_totp(key: str):
    return pyotp.TOTP(key).now()

def get_totp_instance(account_name: str, secret: str | None):
    if secret is None:
        secret == get_otp_key()
    else:
        if len(secret) != 32:
            raise ValueError('Key for 2FA must be 32 characters long')
        if any((char not in base32_charset for char in secret)):
            raise ValueError('Invalid base32 for secret')
    return pyotp.TOTP(secret, digits=8, interval=30, issuer='SenDT', name=account_name)

def get_totp_qr_code(account_name: str, secret: str | None):
    totp = get_totp_instance(account_name, secret)
    
    to_encode = totp.provisioning_uri()
    
    return qrcode.make(to_encode)
    
    