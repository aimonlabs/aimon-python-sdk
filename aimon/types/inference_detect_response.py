# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["InferenceDetectResponse", "InferenceDetectResponseItem"]


class InferenceDetectResponseItem(BaseModel):
    result: Optional[object] = None
    """Result of the detection"""


InferenceDetectResponse = List[InferenceDetectResponseItem]
