# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ModelCreateResponse"]


class ModelCreateResponse(BaseModel):
    description: str

    name: str

    type: str

    id: Optional[str] = None

    company_id: Optional[str] = None

    metadata: Optional[object] = None
