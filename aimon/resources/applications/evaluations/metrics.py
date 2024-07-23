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
from ....types.applications.evaluations import (
    metric_retrieve_params,
    metric_get_evaluation_metrics_params,
    metric_get_evaluation_run_metrics_params,
)
from ....types.applications.evaluations.metric_retrieve_response import MetricRetrieveResponse
from ....types.applications.evaluations.metric_get_evaluation_metrics_response import MetricGetEvaluationMetricsResponse
from ....types.applications.evaluations.metric_get_evaluation_run_metrics_response import (
    MetricGetEvaluationRunMetricsResponse,
)

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
        Fetch metrics for all evaluations of an application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/application/evaluations/metrics",
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

    def get_evaluation_metrics(
        self,
        evaluation_id: str,
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
    ) -> MetricGetEvaluationMetricsResponse:
        """
        Fetch metrics for a specific evaluation of an application

        Args:
          application_name: The name of the application for which metrics are being fetched

          end_timestamp: The end timestamp for filtering metrics data

          start_timestamp: The start timestamp for filtering metrics data

          version: The version of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        return self._get(
            f"/v1/application/evaluations/{evaluation_id}/metrics",
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
                    metric_get_evaluation_metrics_params.MetricGetEvaluationMetricsParams,
                ),
            ),
            cast_to=MetricGetEvaluationMetricsResponse,
        )

    def get_evaluation_run_metrics(
        self,
        evaluation_run_id: str,
        *,
        evaluation_id: str,
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
    ) -> MetricGetEvaluationRunMetricsResponse:
        """
        Fetch metrics for a specific run of a specific evaluation

        Args:
          application_name: The name of the application for which metrics are being fetched

          end_timestamp: The end timestamp for filtering metrics data

          start_timestamp: The start timestamp for filtering metrics data

          version: The version of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        if not evaluation_run_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_run_id` but received {evaluation_run_id!r}")
        return self._get(
            f"/v1/application/evaluations/{evaluation_id}/run/{evaluation_run_id}/metrics",
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
                    metric_get_evaluation_run_metrics_params.MetricGetEvaluationRunMetricsParams,
                ),
            ),
            cast_to=MetricGetEvaluationRunMetricsResponse,
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
        Fetch metrics for all evaluations of an application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/application/evaluations/metrics",
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

    async def get_evaluation_metrics(
        self,
        evaluation_id: str,
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
    ) -> MetricGetEvaluationMetricsResponse:
        """
        Fetch metrics for a specific evaluation of an application

        Args:
          application_name: The name of the application for which metrics are being fetched

          end_timestamp: The end timestamp for filtering metrics data

          start_timestamp: The start timestamp for filtering metrics data

          version: The version of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        return await self._get(
            f"/v1/application/evaluations/{evaluation_id}/metrics",
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
                    metric_get_evaluation_metrics_params.MetricGetEvaluationMetricsParams,
                ),
            ),
            cast_to=MetricGetEvaluationMetricsResponse,
        )

    async def get_evaluation_run_metrics(
        self,
        evaluation_run_id: str,
        *,
        evaluation_id: str,
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
    ) -> MetricGetEvaluationRunMetricsResponse:
        """
        Fetch metrics for a specific run of a specific evaluation

        Args:
          application_name: The name of the application for which metrics are being fetched

          end_timestamp: The end timestamp for filtering metrics data

          start_timestamp: The start timestamp for filtering metrics data

          version: The version of the application

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not evaluation_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_id` but received {evaluation_id!r}")
        if not evaluation_run_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_run_id` but received {evaluation_run_id!r}")
        return await self._get(
            f"/v1/application/evaluations/{evaluation_id}/run/{evaluation_run_id}/metrics",
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
                    metric_get_evaluation_run_metrics_params.MetricGetEvaluationRunMetricsParams,
                ),
            ),
            cast_to=MetricGetEvaluationRunMetricsResponse,
        )


class MetricsResourceWithRawResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = to_raw_response_wrapper(
            metrics.retrieve,
        )
        self.get_evaluation_metrics = to_raw_response_wrapper(
            metrics.get_evaluation_metrics,
        )
        self.get_evaluation_run_metrics = to_raw_response_wrapper(
            metrics.get_evaluation_run_metrics,
        )


class AsyncMetricsResourceWithRawResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = async_to_raw_response_wrapper(
            metrics.retrieve,
        )
        self.get_evaluation_metrics = async_to_raw_response_wrapper(
            metrics.get_evaluation_metrics,
        )
        self.get_evaluation_run_metrics = async_to_raw_response_wrapper(
            metrics.get_evaluation_run_metrics,
        )


class MetricsResourceWithStreamingResponse:
    def __init__(self, metrics: MetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = to_streamed_response_wrapper(
            metrics.retrieve,
        )
        self.get_evaluation_metrics = to_streamed_response_wrapper(
            metrics.get_evaluation_metrics,
        )
        self.get_evaluation_run_metrics = to_streamed_response_wrapper(
            metrics.get_evaluation_run_metrics,
        )


class AsyncMetricsResourceWithStreamingResponse:
    def __init__(self, metrics: AsyncMetricsResource) -> None:
        self._metrics = metrics

        self.retrieve = async_to_streamed_response_wrapper(
            metrics.retrieve,
        )
        self.get_evaluation_metrics = async_to_streamed_response_wrapper(
            metrics.get_evaluation_metrics,
        )
        self.get_evaluation_run_metrics = async_to_streamed_response_wrapper(
            metrics.get_evaluation_run_metrics,
        )
