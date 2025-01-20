# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "InferenceDetectParams",
    "Body",
    "BodyConfig",
    "BodyConfigCompleteness",
    "BodyConfigConciseness",
    "BodyConfigHallucination",
    "BodyConfigHallucinationV0_2",
    "BodyConfigInstructionAdherence",
    "BodyConfigToxicity",
]


class InferenceDetectParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class BodyConfigCompleteness(TypedDict, total=False):
    detector_name: Literal["default"]


class BodyConfigConciseness(TypedDict, total=False):
    detector_name: Literal["default"]


class BodyConfigHallucination(TypedDict, total=False):
    detector_name: Literal["default", "hall_v2"]


class BodyConfigHallucinationV0_2(TypedDict, total=False):
    detector_name: Literal["default"]


class BodyConfigInstructionAdherence(TypedDict, total=False):
    detector_name: Literal["default"]


class BodyConfigToxicity(TypedDict, total=False):
    detector_name: Literal["default"]


class BodyConfig(TypedDict, total=False):
    completeness: BodyConfigCompleteness

    conciseness: BodyConfigConciseness

    hallucination: BodyConfigHallucination

    hallucination_v0_2: Annotated[BodyConfigHallucinationV0_2, PropertyInfo(alias="hallucination_v0.2")]

    instruction_adherence: BodyConfigInstructionAdherence

    toxicity: BodyConfigToxicity


class Body(TypedDict, total=False):
    context: Required[Union[List[str], str]]
    """Context as an array of strings or a single string"""

    generated_text: Required[str]
    """The generated text based on context and user query"""

    application_name: str
    """The application name for publishing metrics."""

    async_mode: bool
    """Indicates whether to run the application in async mode."""

    config: BodyConfig
    """Configuration for the detection"""

    model_name: str
    """The model name for publishing metrics for an application."""

    publish: bool
    """Indicates whether to publish metrics."""

    user_query: str
    """The user's query"""
