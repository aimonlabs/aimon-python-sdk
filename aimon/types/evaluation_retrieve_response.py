# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["EvaluationRetrieveResponse", "EvaluationRetrieveResponseItem"]


class EvaluationRetrieveResponseItem(BaseModel):
    application_id: Optional[str] = None

    evaluation_id: Optional[str] = None

    run_ids: Optional[List[str]] = None


EvaluationRetrieveResponse = List[EvaluationRetrieveResponseItem]
