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

import functools
import re
import unicodedata
import warnings
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, TypeVar

ISO_8601 = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_8601_NO_MS = "%Y-%m-%dT%H:%M:%SZ"
T = TypeVar("T")


def slugify(value):
    value = str(value)
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[:.-/\s]+", "_", value)
    value = re.sub(r"[^\w\s-]", "", value)
    return value


def deprecated(reason=""):
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
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


def raw_required_str(raw_element: dict[str, Any], key: str) -> str:
    value = raw_element[key]
    if not isinstance(value, str):
        raise TypeError(f"expected raw field {key!r} to be str")
    return value


def raw_optional_str(raw_element: dict[str, Any], key: str) -> str | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"expected raw field {key!r} to be str")
    return value


def raw_optional_str_or_float(
    raw_element: dict[str, Any], key: str
) -> str | float | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise TypeError(f"expected raw field {key!r} to be str or float")
    return float(value) if isinstance(value, int | float) else value


def raw_required_int(raw_element: dict[str, Any], key: str) -> int:
    value = raw_element[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be int")
    return value


def raw_optional_int(raw_element: dict[str, Any], key: str) -> int | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be int")
    return value


def raw_required_bool(raw_element: dict[str, Any], key: str) -> bool:
    value = raw_element[key]
    if not isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be bool")
    return value


def raw_optional_bool(raw_element: dict[str, Any], key: str) -> bool | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise TypeError(f"expected raw field {key!r} to be bool")
    return value


def raw_optional_datetime(raw_element: dict[str, Any], key: str) -> datetime | None:
    value = raw_element.get(key)
    if value is None:
        return None
    return _raw_datetime(value, key)


def raw_required_datetime(raw_element: dict[str, Any], key: str) -> datetime:
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
    raw_element: dict[str, Any], key: str, factory: Callable[[dict[str, Any]], T]
) -> T | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return factory(value)


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
