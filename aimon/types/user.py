# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["User"]


class User(BaseModel):
    id: str

    email: str

    phone: str

    username: str

    auth0_id: Optional[str] = None

    bio: Optional[str] = None

    company_id: Optional[str] = None

    date_joined: Optional[datetime] = None

    first_name: Optional[str] = FieldInfo(alias="firstName", default=None)

    is_active: Optional[bool] = None

    is_staff: Optional[bool] = None

    is_superuser: Optional[bool] = None

    last_login: Optional[datetime] = None

    last_name: Optional[str] = FieldInfo(alias="lastName", default=None)

    user_status: Optional[int] = FieldInfo(alias="userStatus", default=None)
