# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["InferenceDetectParams", "Body", "BodyConfig"]


class InferenceDetectParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class BodyConfig(TypedDict, total=False):
    completeness: Literal["default"]

    conciseness: Literal["default"]

    hallucination: Literal["default", "hall_v2"]

    hallucination_v0_2: Annotated[Literal["default"], PropertyInfo(alias="hallucination_v0.2")]

    instruction_adherence: Literal["default"]

    toxicity: Literal["default"]


class Body(TypedDict, total=False):
    context: Required[Union[List[str], str]]
    """Context as an array of strings or a single string"""

    generated_text: Required[str]
    """The generated text based on context and user query"""

    config: BodyConfig
    """Configuration for the detection"""

    user_query: str
    """The user's query"""
