from os import PathLike
from typing import TypeVar
from typing_extensions import TypeAlias

# Use for "self" annotations:
#   def __enter__(self: Self) -> Self: ...
Self = TypeVar("Self")  # noqa: Y001

StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes]  # stable
