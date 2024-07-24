# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.applications.production import metric_retrieve_params
from ....types.applications.production.metric_retrieve_response import MetricRetrieveResponse

__all__ = ["MetricsResource", "AsyncMetricsResource"]


class MetricsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MetricsResourceWithRawResponse:
        return MetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MetricsResourceWithStreamingResponse:
        return MetricsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        application_name: str,
        end_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        start_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MetricRetrieveResponse:
        """
        Fetch production metrics of an application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/application/production/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "application_name": application_name,
                        "end_timestamp": end_timestamp,
                        "start_timestamp": start_timestamp,
                        "version": version,
                    },
                    metric_retrieve_params.MetricRetrieveParams,
                ),
            ),
            cast_to=MetricRetrieveResponse,
        )


class AsyncMetricsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMetricsResourceWithRawResponse:
        return AsyncMetricsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMetricsResourceWithStreamingResponse:
        return AsyncMetricsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        application_name: str,
        end_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        start_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MetricRetrieveResponse:
        """
        Fetch production metrics of an application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/application/production/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "application_name": application_name,
                        "end_timestamp": end_timestamp,
                        "start_timestamp": start_timestamp,
                        "version": version,
                    },
                    metric_retrieve_params.MetricRetrieveParams,
                ),
            ),
            cast_to=MetricRetrieveResponse,
        )


class MetricsResourceWithRawResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = to_raw_response_wrapper(
            metrics.retrieve,
        )


class AsyncMetricsResourceWithRawResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = async_to_raw_response_wrapper(
            metrics.retrieve,
        )


class MetricsResourceWithStreamingResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = to_streamed_response_wrapper(
            metrics.retrieve,
        )


class AsyncMetricsResourceWithStreamingResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = async_to_streamed_response_wrapper(
            metrics.retrieve,
        )
