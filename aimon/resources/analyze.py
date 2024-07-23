# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import analyze_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.analyze_create_response import AnalyzeCreateResponse

__all__ = ["AnalyzeResource", "AsyncAnalyzeResource"]


class AnalyzeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AnalyzeResourceWithRawResponse:
        return AnalyzeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AnalyzeResourceWithStreamingResponse:
        return AnalyzeResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        body: Iterable[analyze_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnalyzeCreateResponse:
        """
        Save and compute metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/save-compute-metrics",
            body=maybe_transform(body, analyze_create_params.AnalyzeCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnalyzeCreateResponse,
        )


class AsyncAnalyzeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAnalyzeResourceWithRawResponse:
        return AsyncAnalyzeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAnalyzeResourceWithStreamingResponse:
        return AsyncAnalyzeResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        body: Iterable[analyze_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnalyzeCreateResponse:
        """
        Save and compute metrics

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/save-compute-metrics",
            body=await async_maybe_transform(body, analyze_create_params.AnalyzeCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnalyzeCreateResponse,
        )


class AnalyzeResourceWithRawResponse:
    def __init__(self, analyze: AnalyzeResource) -> None:
        self._analyze = analyze

        self.create = to_raw_response_wrapper(
            analyze.create,
        )


class AsyncAnalyzeResourceWithRawResponse:
    def __init__(self, analyze: AsyncAnalyzeResource) -> None:
        self._analyze = analyze

        self.create = async_to_raw_response_wrapper(
            analyze.create,
        )


class AnalyzeResourceWithStreamingResponse:
    def __init__(self, analyze: AnalyzeResource) -> None:
        self._analyze = analyze

        self.create = to_streamed_response_wrapper(
            analyze.create,
        )


class AsyncAnalyzeResourceWithStreamingResponse:
    def __init__(self, analyze: AsyncAnalyzeResource) -> None:
        self._analyze = analyze

        self.create = async_to_streamed_response_wrapper(
            analyze.create,
        )
