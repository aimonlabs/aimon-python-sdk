# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.evaluations import run_create_params
from ...types.evaluations.run_create_response import RunCreateResponse

__all__ = ["RunResource", "AsyncRunResource"]


class RunResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RunResourceWithRawResponse:
        return RunResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunResourceWithStreamingResponse:
        return RunResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        evaluation_id: str,
        id: str | NotGiven = NOT_GIVEN,
        completed_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        creation_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        metrics_config: object | NotGiven = NOT_GIVEN,
        metrics_path: str | NotGiven = NOT_GIVEN,
        model_output_path: str | NotGiven = NOT_GIVEN,
        run_number: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """
        Create a new evaluation run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/evaluation-run",
            body=maybe_transform(
                {
                    "evaluation_id": evaluation_id,
                    "id": id,
                    "completed_time": completed_time,
                    "creation_time": creation_time,
                    "metadata": metadata,
                    "metrics_config": metrics_config,
                    "metrics_path": metrics_path,
                    "model_output_path": model_output_path,
                    "run_number": run_number,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )


class AsyncRunResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRunResourceWithRawResponse:
        return AsyncRunResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunResourceWithStreamingResponse:
        return AsyncRunResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        evaluation_id: str,
        id: str | NotGiven = NOT_GIVEN,
        completed_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        creation_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        metrics_config: object | NotGiven = NOT_GIVEN,
        metrics_path: str | NotGiven = NOT_GIVEN,
        model_output_path: str | NotGiven = NOT_GIVEN,
        run_number: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """
        Create a new evaluation run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/evaluation-run",
            body=await async_maybe_transform(
                {
                    "evaluation_id": evaluation_id,
                    "id": id,
                    "completed_time": completed_time,
                    "creation_time": creation_time,
                    "metadata": metadata,
                    "metrics_config": metrics_config,
                    "metrics_path": metrics_path,
                    "model_output_path": model_output_path,
                    "run_number": run_number,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )


class RunResourceWithRawResponse:
    def __init__(self, run: RunResource) -> None:
        self._run = run

        self.create = to_raw_response_wrapper(
            run.create,
        )


class AsyncRunResourceWithRawResponse:
    def __init__(self, run: AsyncRunResource) -> None:
        self._run = run

        self.create = async_to_raw_response_wrapper(
            run.create,
        )


class RunResourceWithStreamingResponse:
    def __init__(self, run: RunResource) -> None:
        self._run = run

        self.create = to_streamed_response_wrapper(
            run.create,
        )


class AsyncRunResourceWithStreamingResponse:
    def __init__(self, run: AsyncRunResource) -> None:
        self._run = run

        self.create = async_to_streamed_response_wrapper(
            run.create,
        )
