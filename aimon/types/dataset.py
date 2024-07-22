# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Dataset"]


class Dataset(BaseModel):
    description: str

    name: str

    id: Optional[str] = None

    company_id: Optional[str] = None

    creation_time: Optional[datetime] = None

    last_updated_time: Optional[datetime] = None

    s3_location: Optional[str] = None

    sha: Optional[str] = None

    user_id: Optional[str] = None
