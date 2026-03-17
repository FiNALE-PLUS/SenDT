from fastapi import status

from fastapi import HTTPException


bad_credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

two_factor_enabled_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication has already been verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

two_factor_disabled_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication has not been verified",
            headers={"WWW-Authenticate": "Bearer"},
        )