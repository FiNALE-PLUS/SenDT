from abc import ABC, abstractmethod
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class AbstractQuotedString(str, ABC):
    """
    Ensures that a string is surrounded by ``_quote_str``,
    optionally preceded by ``_prefix`` and followed by ``_suffix``.
    If this is not the case, it adds them. if ``_quote_str`` is found within the string,
    a ``ValueError`` is raised.
    """

    @classmethod
    @property
    def _value_prefix(cls) -> str:
        return ((str(cls._prefix) if cls._prefix is not None else '')
                + str(cls._quote_str))

    @classmethod
    @property
    def _value_suffix(cls) -> str:
        return (str(cls._quote_str)
                + (str(cls._suffix) if cls._suffix is not None else ''))

    @property
    @abstractmethod
    def _quote_str(self) -> str:
        return ''

    @property
    @abstractmethod
    def _prefix(self) -> str | None:
        return ''

    @property
    @abstractmethod
    def _suffix(self) -> str | None:
        return ''

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # TODO: Modify to include quote validation over in __new__

        return core_schema.chain_schema(
            [
                handler.generate_schema(str),
                core_schema.no_info_plain_validator_function(
                    function=cls.try_validate_string,
                )
            ]
        )

    @classmethod
    def try_validate_string(cls, v: str):
        if not isinstance(v, str):
            raise TypeError(f"Pydantic coercion has not occurred before {cls.__name__}'s validation. "
                            f"Please check the validation logic and fix this error.")
        # Use the quoted string's internal validation and value mutation
        return cls.__new__(cls, content=v)

    def __new__(cls, content):
        initial_value = super().__new__(cls, content)

        # Value is already quoted correctly,
        if (initial_value.startswith(cls._value_prefix)
                and initial_value.endswith(cls._value_suffix)):
            # And is not within the contained value
            if cls._quote_str not in initial_value[len(cls._value_prefix):-len(cls._value_suffix)]:
                return initial_value
        # Unquoted values that *do not* contain the quote string
        if (not initial_value.startswith(cls._value_prefix)
                and not initial_value.endswith(cls._value_suffix)
                and str(cls._quote_str) not in initial_value):
            return cls._value_prefix + initial_value + cls._value_suffix

        if str(cls._quote_str) in initial_value:
            raise ValueError(
                f"A `{cls._quote_str}` has been found within the body of a string to be quoted by {cls.__name__}. "
                f"(value given: {initial_value})")
        else:
            raise ValueError(f"An invalid value has been passed to {cls.__name__} to be quoted. "
                             f"(value given: {initial_value})")

    @classmethod
    def remove_quotes(cls, string: str) -> str:
        guaranteed_quoted_string = cls(string)

        return guaranteed_quoted_string[
            len(cls._value_prefix) if string.startswith(cls._value_prefix) else 0
            :-len(cls._value_suffix) if string.endswith(cls._value_suffix) else len(string)
        ]


class DoubleQuotedString(AbstractQuotedString):
    _quote_str = r'"'
    _prefix = None
    _suffix = None


class TextoutQuotedString(DoubleQuotedString):
    _prefix = r'L'
