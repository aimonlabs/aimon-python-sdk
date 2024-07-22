# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ApplicationCreateParams"]


class ApplicationCreateParams(TypedDict, total=False):
    model_name: Required[str]

    name: Required[str]

    type: Required[str]

    id: str

    company_id: str

    context_source_id: str

    last_query_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    metadata: object

    model_id: str

    stage: str

    user_id: str

    version: str
