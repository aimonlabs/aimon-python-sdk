# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["MetricRetrieveParams"]


class MetricRetrieveParams(TypedDict, total=False):
    application_name: Required[str]

    end_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    start_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    version: str
