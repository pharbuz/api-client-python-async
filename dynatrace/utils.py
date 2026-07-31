"""
Copyright 2021 Dynatrace LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import functools
import re
import unicodedata
import warnings
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ParamSpec, Protocol, TypeAlias, TypeVar, cast, runtime_checkable

ISO_8601 = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_8601_NO_MS = "%Y-%m-%dT%H:%M:%SZ"
JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONDict: TypeAlias = dict[str, JSONValue]
JSONMapping: TypeAlias = Mapping[str, JSONValue]
P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
TEnum = TypeVar("TEnum", bound=Enum)


@runtime_checkable
class JsonSerializable(Protocol):
    def to_json(self) -> JSONDict: ...


def slugify(value: object) -> str:
    value = str(value)
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[:.-/\s]+", "_", value)
    value = re.sub(r"[^\w\s-]", "", value)
    return value


def deprecated(reason: str = "") -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def new_func(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(
                f"'{func.__name__}' is deprecated. {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return new_func

    return decorator


def timestamp_to_string(timestamp: datetime | str | None) -> str | None:
    if not isinstance(timestamp, datetime):
        return timestamp
    return (
        timestamp.astimezone(timezone.utc)
        .replace(tzinfo=None)
        .isoformat(timespec="milliseconds")
    )


def iso8601_to_datetime(timestamp: str | None) -> datetime | None:
    if isinstance(timestamp, str):
        try:
            return datetime.strptime(timestamp, ISO_8601)
        except ValueError:
            # DT API currently omitts milliseconds in response if they are 000
            return datetime.strptime(timestamp, ISO_8601_NO_MS)
    return timestamp


def int64_to_datetime(timestamp: int | None) -> datetime | None:
    if timestamp is None or not timestamp:
        return None
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc)


def raw_required_str(raw_element: JSONMapping, key: str) -> str:
    """Return a required raw field as a string."""
    value = raw_element[key]
    if not isinstance(value, str):
        raise TypeError(f"expected raw field {key!r} to be str")
    return value


def raw_optional_str(raw_element: JSONMapping, key: str) -> str | None:
    """Return an optional raw field as a string, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"expected raw field {key!r} to be str")
    return value


def raw_optional_str_list(raw_element: JSONMapping, key: str) -> list[str]:
    """Return an optional raw field as a string list, defaulting to an empty list."""
    value = raw_element.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[str]")
    return cast(list[str], value)


def raw_required_str_list(raw_element: JSONMapping, key: str) -> list[str]:
    """Return a required raw field as a string list."""
    value = raw_element[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[str]")
    return cast(list[str], value)


def raw_optional_str_list_or_none(
    raw_element: JSONMapping, key: str
) -> list[str] | None:
    """Return an optional raw field as a string list, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[str]")
    return cast(list[str], value)


def raw_optional_enum_or_str(
    enum_type: type[TEnum], raw_value: Any
) -> TEnum | str | None:
    """Return an optional raw enum value, preserving unknown string values."""
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise TypeError(
            f"expected enum value to be str, got {type(raw_value).__name__}"
        )
    try:
        return enum_type(raw_value)
    except ValueError:
        return raw_value


def raw_optional_str_or_float(raw_element: JSONMapping, key: str) -> str | float | None:
    """Return an optional raw field as a string or float, or None when missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise TypeError(f"expected raw field {key!r} to be str or float")
    return float(value) if isinstance(value, int | float) else value


def raw_optional_float(raw_element: JSONMapping, key: str) -> float | None:
    """Return an optional raw field as a float, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"expected raw field {key!r} to be float")
    return float(value)


def raw_optional_dict(raw_element: JSONMapping, key: str) -> dict[str, Any] | None:
    """Return an optional raw field as a dictionary, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return cast(dict[str, Any], value)


def raw_optional_str_dict(raw_element: JSONMapping, key: str) -> dict[str, str] | None:
    """Return an optional raw field as a string-to-string dictionary."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    result: dict[str, str] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str):
            raise TypeError(f"expected raw field {key!r} keys to be str")
        if not isinstance(item_value, str):
            raise TypeError(f"expected raw field {key!r} values to be str")
        result[item_key] = item_value
    return result


def raw_optional_float_dict(
    raw_element: JSONMapping, key: str
) -> dict[str, float] | None:
    """Return an optional raw field as a string-to-float dictionary."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    result: dict[str, float] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str):
            raise TypeError(f"expected raw field {key!r} keys to be str")
        if isinstance(item_value, bool) or not isinstance(item_value, int | float):
            raise TypeError(f"expected raw field {key!r} values to be float")
        result[item_key] = float(item_value)
    return result


def raw_required_int(raw_element: JSONMapping, key: str) -> int:
    """Return a required raw field as an integer."""
    value = raw_element[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be int")
    return value


def raw_required_float(raw_element: JSONMapping, key: str) -> float:
    """Return a required raw field as a float."""
    value = raw_element[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"expected raw field {key!r} to be float")
    return float(value)


def raw_optional_int(raw_element: JSONMapping, key: str) -> int | None:
    """Return an optional raw field as an integer, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be int")
    return value


def raw_required_bool(raw_element: JSONMapping, key: str) -> bool:
    """Return a required raw field as a boolean."""
    value = raw_element[key]
    if not isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be bool")
    return value


def raw_optional_bool(raw_element: JSONMapping, key: str) -> bool | None:
    """Return an optional raw field as a boolean, or None when it is missing."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be bool")
    return value


def raw_optional_datetime(raw_element: JSONMapping, key: str) -> datetime | None:
    """Return an optional raw timestamp field as a UTC datetime."""
    value = raw_element.get(key)
    if value is None:
        return None
    return _raw_datetime(value, key)


def raw_required_datetime(raw_element: JSONMapping, key: str) -> datetime:
    """Return a required raw timestamp field as a UTC datetime."""
    return _raw_datetime(raw_element[key], key)


def _raw_datetime(value: Any, key: str) -> datetime:
    if isinstance(value, int) and not isinstance(value, bool):
        converted = int64_to_datetime(value)
        if converted is None:
            raise ValueError(f"expected raw field {key!r} to be a non-zero timestamp")
        return converted
    if isinstance(value, str):
        converted = int64_to_datetime(int(value))
        if converted is None:
            raise ValueError(f"expected raw field {key!r} to be a non-zero timestamp")
        return converted
    raise TypeError(f"expected raw field {key!r} to be timestamp")


def raw_optional_object(
    raw_element: JSONMapping, key: str, factory: Callable[[JSONDict], T]
) -> T | None:
    """Return an optional raw object field transformed by the provided factory."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return factory(value)


def raw_required_object(
    raw_element: JSONMapping, key: str, factory: Callable[[JSONDict], T]
) -> T:
    """Return a required raw object field transformed by the provided factory."""
    value = raw_element[key]
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return factory(value)


def raw_optional_object_list(
    raw_element: JSONMapping, key: str, factory: Callable[[JSONDict], T]
) -> list[T] | None:
    """Return an optional raw object list transformed by the provided factory."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[object]")
    return [factory(cast(JSONDict, item)) for item in value]


def raw_required_object_list(
    raw_element: JSONMapping, key: str, factory: Callable[[JSONDict], T]
) -> list[T]:
    """Return a required raw object list transformed by the provided factory."""
    value = raw_element[key]
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[object]")
    return [factory(cast(JSONDict, item)) for item in value]


def raw_optional_object_dict(
    raw_element: JSONMapping, key: str, factory: Callable[[JSONDict], T]
) -> dict[str, T] | None:
    """Return an optional raw object dictionary transformed by the provided factory."""
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    result: dict[str, T] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str):
            raise TypeError(f"expected raw field {key!r} keys to be str")
        if not isinstance(item_value, dict):
            raise TypeError(f"expected raw field {key!r} values to be object")
        result[item_key] = factory(item_value)
    return result


def datetime_to_int64(timestamp: datetime | int | str | None) -> int | str | None:
    if not isinstance(timestamp, datetime):
        return timestamp
    return int(timestamp.replace(tzinfo=timezone.utc).timestamp() * 1000)


def bool_header_value(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


def build_headers(
    dt_client_context: str | None = None,
    enforce_query_consumption_limit_header: bool | None = None,
) -> dict[str, str] | None:
    headers: dict[str, str] = {}
    if dt_client_context is not None:
        headers["dt-client-context"] = dt_client_context
    if enforce_query_consumption_limit_header is not None:
        headers["enforce-query-consumption-limit"] = (
            "true" if enforce_query_consumption_limit_header else "false"
        )
    return headers or None
