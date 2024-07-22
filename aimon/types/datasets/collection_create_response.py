# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["CollectionCreateResponse"]


class CollectionCreateResponse(BaseModel):
    dataset_ids: List[str]
    """A list of dataset IDs included in this collection."""

    name: str

    id: Optional[str] = None

    company_id: Optional[str] = None

    creation_time: Optional[datetime] = None

    description: Optional[str] = None

    last_updated_time: Optional[datetime] = None

    user_id: Optional[str] = None
