# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelCreateParams"]


class ModelCreateParams(TypedDict, total=False):
    description: Required[str]

    name: Required[str]

    type: Required[str]

    id: str

    company_id: str

    metadata: object
