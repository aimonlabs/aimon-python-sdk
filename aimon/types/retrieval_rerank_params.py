# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["RetrievalRerankParams"]


class RetrievalRerankParams(TypedDict, total=False):
    context_docs: Required[List[str]]
    """List of context documents."""

    queries: Required[List[str]]
    """List of queries."""

    task_definition: Required[str]
    """Description of the task to guide relevance ranking."""

    model_type: str
    """Optional model type to be used for reranking."""
