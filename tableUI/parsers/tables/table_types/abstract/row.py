from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class TableRow(BaseModel, ABC):
    comment: Optional[str] = None
    # Explicitly throw an error when an extra field is attempted to be loaded into a row object
    model_config = ConfigDict(extra="forbid")

    @property
    def column_count(self) -> int:
        return len([field for field in self.__class__.model_fields.values() if field.validation_alias is not None])

    @property
    def column_widths(self) -> list[int]:
        fields = self.coerce_model_field_values([
            getattr(self, k) for k, field in list(self.__class__.model_fields.items())
            if field.validation_alias is not None
        ])
        # Get all field names, then get the lengths of the values stored in each found field
        # widths = [len(str(getattr(self, k))) for k, field in list(self.__class__.model_fields.items())
        #           if field.validation_alias is not None]
        return [len(i) for i in fields]

    @classmethod
    def get_table_column_string(cls, table_name: str, include_trailing_comma: bool) -> str:
        column_names = [field.validation_alias.choices[1] for field in cls.model_fields.values() if
                        field.validation_alias is not None]
        return f'/// @note {table_name}( {", ".join(column_names)}{"," if include_trailing_comma else ""} )'

    # @classmethod
    # @abstractmethod
    # def get_table_column_string(cls) -> str:
    #     ...

    # TODO: refactor to classmethod or function
    def coerce_model_field_values(self, model_field_values: list[Any]) -> list[str]:
        coerced_model_field_values = []

        for field_value in model_field_values:
            coerced_value = field_value
            # Booleans are represented as 0 or 1
            if isinstance(field_value, bool):
                coerced_value = int(field_value)
            # Remove decimal from number if not necessary
            elif isinstance(field_value, float):
                if field_value.is_integer():
                    coerced_value = int(field_value)
            elif isinstance(field_value, Decimal):
                if field_value % 1 == 0:
                    coerced_value = int(field_value)
            # Stringify regardless of coercion done
            coerced_model_field_values.append(str(coerced_value))

        return coerced_model_field_values

    def get_table_column_values(self) -> list[str]:
        model_field_values = [getattr(self, field_name)
                              for field_name, field in self.__class__.model_fields.items()
                              if field.validation_alias is not None]

        # Booleans are coerced to 0 or 1, and all other values are coerced to their string equivalents

        return self.coerce_model_field_values(model_field_values)

    def _get_table_row(self, table_name: str) -> str:
        return self.get_plain_table_row(
            table_name,
            *(0 for _ in range(self.column_count))
        )

    # @abstractmethod
    # def get_table_row(self) -> str:
    #     ...

    def get_plain_table_row(self, table_name: str, trailing_comma_required: bool, *column_widths: int) -> str:
        table_column_values = self.get_table_column_values()

        if len(column_widths) != len(table_column_values):
            raise ValueError(
                f"{len(table_column_values)} column widths required for this table (got {len(column_widths)})")

        return (f'{table_name}( {" ".join([f"{str(column)
                                              + (',' if idx != len(table_column_values) - 1 else '')
                                              + '':<{column_widths[idx]
                                                     + (1 if idx != len(table_column_values) - 1 else 0)}}"
                                           for idx, column in enumerate(table_column_values)])}'
                f'{"," if trailing_comma_required else ''} )'
                f'{" ///< " + self.comment if self.comment is not None else ''}')

    # @abstractmethod
    # def get_spaced_table_row(self, table_name: str, *column_widths: int) -> str:
    #     ...
