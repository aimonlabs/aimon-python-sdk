# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MetricRetrieveResponse", "Evaluation"]


class Evaluation(BaseModel):
    metric_name: Optional[str] = FieldInfo(alias="metricName", default=None)

    timestamp: Optional[datetime] = None

    value: Optional[float] = None


class MetricRetrieveResponse(BaseModel):
    evaluations: Optional[List[Evaluation]] = None
