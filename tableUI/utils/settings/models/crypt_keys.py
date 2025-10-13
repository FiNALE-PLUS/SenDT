from typing import Annotated, Self

from pydantic import BaseModel, StringConstraints, model_validator

DataEncryptionKey = Annotated[str, StringConstraints(pattern="^[0-9a-fA-F]{32}$")]


class CryptKeySettings(BaseModel, validate_assignment=True):
    default_key: str | None = None
    crypt_keys: dict[str, DataEncryptionKey] = {}

    @model_validator(mode='after')
    def check_default_key_is_valid(self) -> Self:
        if self.default_key is not None and self.crypt_keys.get(self.default_key) is None:
            raise ValueError('An invalid default key selection was provided.')
        return self

    def add_key(self, key_name: str, key_value: str) -> None:
        if key_name in self.crypt_keys:
            raise KeyError(f'A key with the name `{key_name}` already exists in the current set of crypt keys.')

        cur_keys = self.crypt_keys
        cur_keys[key_name] = key_value
        self.crypt_keys = cur_keys

    def remove_crypt_key_with_name(self, key_name: str):
        """
        Recommended method to remove a crypt key in ``SenDTSettings``.
        Ensures that validation is run when attempting to remove a crypt key,
        raising a validation error if the key to remove is set as the default.
        If the default key is to be removed, the default should be replaced or set to ``None`` explicitly.

        :param key_name: The name of the crypt key to remove.
        """
        keys_after_removal = self.crypt_keys
        keys_after_removal.pop(key_name)
        self.crypt_keys = keys_after_removal