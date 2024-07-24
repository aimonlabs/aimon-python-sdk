# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["MetricGetEvaluationMetricsParams"]


class MetricGetEvaluationMetricsParams(TypedDict, total=False):
    application_name: Required[str]
    """The name of the application for which metrics are being fetched"""

    end_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """The end timestamp for filtering metrics data"""

    start_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """The start timestamp for filtering metrics data"""

    version: str
    """The version of the application"""
