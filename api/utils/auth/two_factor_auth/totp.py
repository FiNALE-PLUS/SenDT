import pyotp
import qrcode

def get_otp_key():
    return pyotp.random_base32()

def get_totp_instance(account_name: str):
    return pyotp.TOTP(get_otp_key(), digits=8, interval=30, issuer='SenDT', name=account_name)

def get_totp_qr_code(account_name: str):
    totp = get_totp_instance(account_name)
    
    to_encode = totp.provisioning_uri()
    print(to_encode)
    
    return qrcode.make(to_encode)
    
    