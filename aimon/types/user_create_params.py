# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    id: Required[str]

    email: Required[str]

    phone: Required[str]

    username: Required[str]

    auth0_id: str

    bio: str

    company_id: str

    date_joined: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    is_active: bool

    is_staff: bool

    is_superuser: bool

    last_login: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    user_status: Annotated[int, PropertyInfo(alias="userStatus")]
