# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluationCreateResponse"]


class EvaluationCreateResponse(BaseModel):
    application_id: str

    dataset_collection_id: str

    api_model_id: str = FieldInfo(alias="model_id")

    name: str

    id: Optional[str] = None

    end_time: Optional[datetime] = None

    metadata: Optional[object] = None

    start_time: Optional[datetime] = None
