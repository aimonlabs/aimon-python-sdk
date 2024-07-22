# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The CSV file containing the dataset"""

    json_data: Required[str]
    """JSON string containing dataset metadata"""
