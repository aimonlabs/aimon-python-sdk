# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RunCreateResponse"]


class RunCreateResponse(BaseModel):
    evaluation_id: str

    id: Optional[str] = None

    completed_time: Optional[datetime] = None

    creation_time: Optional[datetime] = None

    metadata: Optional[object] = None

    metrics_config: Optional[object] = None

    metrics_path: Optional[str] = None

    api_model_output_path: Optional[str] = FieldInfo(alias="model_output_path", default=None)

    run_number: Optional[int] = None
