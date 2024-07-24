# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["RunCreateParams"]


class RunCreateParams(TypedDict, total=False):
    evaluation_id: Required[str]

    id: str

    completed_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    creation_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    metadata: object

    metrics_config: object

    metrics_path: str

    model_output_path: str

    run_number: int
