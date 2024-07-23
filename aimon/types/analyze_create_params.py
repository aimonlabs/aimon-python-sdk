# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["AnalyzeCreateParams", "Body"]


class AnalyzeCreateParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    application_id: Required[str]

    context_docs: Required[List[str]]

    output: Required[str]

    prompt: Required[str]

    user_query: Required[str]

    version: Required[str]

    evaluation_id: Optional[str]

    evaluation_run_id: Optional[str]
