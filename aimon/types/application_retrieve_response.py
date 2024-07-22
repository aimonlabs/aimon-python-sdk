# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ApplicationRetrieveResponse"]


class ApplicationRetrieveResponse(BaseModel):
    api_model_name: str = FieldInfo(alias="model_name")

    name: str

    type: str

    id: Optional[str] = None

    company_id: Optional[str] = None

    context_source_id: Optional[str] = None

    last_query_timestamp: Optional[datetime] = None

    metadata: Optional[object] = None

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)

    stage: Optional[str] = None

    user_id: Optional[str] = None

    version: Optional[str] = None
