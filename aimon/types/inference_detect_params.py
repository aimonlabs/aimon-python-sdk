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

    config: BodyConfig
    """Configuration for the detection"""

    user_query: str
    """The user's query"""

    publish: bool
    """If True, the payload will be published to AIMon and can be viewed on the AIMon UI. Default is False."""

    async_mode: bool
    """If True, the detect() function will return immediately with a DetectResult object. Default is False."""

    application_name: str
    """Application name"""

    model_name: str
    """Model name"""