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
from datetime import UTC, datetime

ISO_8601 = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_8601_NO_MS = "%Y-%m-%dT%H:%M:%SZ"


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
        timestamp.astimezone(UTC)
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
    return datetime.fromtimestamp(timestamp / 1000, UTC)


def datetime_to_int64(timestamp: datetime | None) -> int | None:
    if not isinstance(timestamp, datetime):
        return timestamp
    return int(timestamp.replace(tzinfo=UTC).timestamp() * 1000)


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
        headers["enforce-query-consumption-limit"] = bool_header_value(
            enforce_query_consumption_limit_header
        )
    return headers or None
