# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ...types.datasets import record_list_params
from ...types.datasets.record_list_response import RecordListResponse

__all__ = ["RecordsResource", "AsyncRecordsResource"]


class RecordsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RecordsResourceWithRawResponse:
        return RecordsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RecordsResourceWithStreamingResponse:
        return RecordsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        sha: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RecordListResponse:
        """
        Get dataset records by SHA

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/dataset-records",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"sha": sha}, record_list_params.RecordListParams),
            ),
            cast_to=RecordListResponse,
        )


class AsyncRecordsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRecordsResourceWithRawResponse:
        return AsyncRecordsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRecordsResourceWithStreamingResponse:
        return AsyncRecordsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        sha: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RecordListResponse:
        """
        Get dataset records by SHA

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/dataset-records",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"sha": sha}, record_list_params.RecordListParams),
            ),
            cast_to=RecordListResponse,
        )


class RecordsResourceWithRawResponse:
    def __init__(self, records: RecordsResource) -> None:
        self._records = records

        self.list = to_raw_response_wrapper(
            records.list,
        )


class AsyncRecordsResourceWithRawResponse:
    def __init__(self, records: AsyncRecordsResource) -> None:
        self._records = records

        self.list = async_to_raw_response_wrapper(
            records.list,
        )


class RecordsResourceWithStreamingResponse:
    def __init__(self, records: RecordsResource) -> None:
        self._records = records

        self.list = to_streamed_response_wrapper(
            records.list,
        )


class AsyncRecordsResourceWithStreamingResponse:
    def __init__(self, records: AsyncRecordsResource) -> None:
        self._records = records

        self.list = async_to_streamed_response_wrapper(
            records.list,
        )
