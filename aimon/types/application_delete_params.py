# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ApplicationDeleteParams"]


class ApplicationDeleteParams(TypedDict, total=False):
    name: Required[str]
    """The name of the application to delete"""

    stage: Required[str]
    """The stage of the application (e.g., production, evaluation)"""

    version: Required[str]
    """The version of the application to delete"""
