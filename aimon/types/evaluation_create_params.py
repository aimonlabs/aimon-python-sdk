# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationCreateParams"]


class EvaluationCreateParams(TypedDict, total=False):
    application_id: Required[str]

    dataset_collection_id: Required[str]

    model_id: Required[str]

    name: Required[str]

    id: str

    end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    metadata: object

    start_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
