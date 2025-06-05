# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The CSV file containing the dataset"""

    name: Required[str]
    """Name of the dataset"""

    description: str
    """Optional description of the dataset"""