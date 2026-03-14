from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class ScopeField(BaseModel, ABC):
    ScopeName: ClassVar[str] = 'TODO'
    
    @abstractmethod
    def get_scope_values(self) -> list[str]:
        """
        Used to get a scope field's individual scope values. Scopes that only return a single scope must return a list containing said singular scope.

        Returns:
            list[str]: A list of all scope values that should be included within the ``scope`` field of the relevant JWT
        """
        ...
    
    @abstractmethod
    def from_token_scope_string(self, token_scope_string: str) -> None:
        """
        Mutates the scope field to match its state with any relevant scopes from a JWT. Accepts the value of the token's ``scope`` field as-is.

        Args:
            token_scope_string (str): The full ``scope`` value of the token to match scopes of.
        """
        ...
        
    @abstractmethod
    def openapi_scope_descriptions(self) -> dict[str, str]:
        """
        Generates a dictionary containing the scope names and descriptions for the current field to be inserted into authentication docs.

        Returns:
            dict[str, str]: A dictionary of keys representing the individual stringified scopes, and values designating the documentation for the respective scope.
        """
        ...