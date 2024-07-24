# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CollectionCreateParams"]


class CollectionCreateParams(TypedDict, total=False):
    dataset_ids: Required[List[str]]
    """A list of dataset IDs included in this collection."""

    name: Required[str]

    id: str

    company_id: str

    creation_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    description: str

    last_updated_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    user_id: str
