# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MetricGetEvaluationMetricsResponse", "Evaluation"]


class Evaluation(BaseModel):
    metric_name: Optional[str] = FieldInfo(alias="metricName", default=None)
    """The name of the metric"""

    timestamp: Optional[datetime] = None
    """The timestamp when the metric was recorded"""

    value: Optional[float] = None
    """The value of the metric"""


class MetricGetEvaluationMetricsResponse(BaseModel):
    evaluations: Optional[List[Evaluation]] = None
