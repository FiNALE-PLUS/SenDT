from enum import Enum

from dialects.abstract.finale import SDTSlidePattern


class ChartError(Exception):
    def __init__(self, message: str, chart_line: str | None = None):
        self.message = message
        self.chart_line = chart_line

    def __str__(self):
        return f"{self.message}" + f"  (chart fragment: {self.chart_line})" if self.chart_line is not None else ""


class ChartDialect(Enum):
    Sentakki = 1


class ChartDialectError(ChartError):
    def __init__(self, dialect: ChartDialect, message: str, chart_line: str):
        super(ChartDialectError, self).__init__(message, chart_line)
        self.dialect = dialect

    def __str__(self):
        return f"Please ensure this chart is a {self.dialect.name} chart. " + super().__str__()


class ChartFeatureError(ChartError):
    pass


class ChartSlideError(ChartError):
    pass


class ChartGrandVError(ChartSlideError):
    pass


class ChartSlidePathError(ChartSlideError):
    pass


class InvalidReturningSlidePatternError(ChartSlidePathError):
    def __init__(self, slide_pattern: SDTSlidePattern):
        self.slide_pattern = slide_pattern

    def __str__(self):
        return f"{self.slide_pattern.name} cannot return to its starting point."


class ChartWarning(UserWarning):
    pass


class ChartFeatureWarning(ChartWarning):
    pass


class ChartUserWarning(ChartWarning):
    """Used to denote a warning intended for a user to look over within the source.
    Generally a result of an element that is valid, but may be unintentionally included."""
    pass
