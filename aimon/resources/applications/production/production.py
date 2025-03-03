# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .metrics import (
    MetricsResource,
    AsyncMetricsResource,
    MetricsResourceWithRawResponse,
    AsyncMetricsResourceWithRawResponse,
    MetricsResourceWithStreamingResponse,
    AsyncMetricsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ProductionResource", "AsyncProductionResource"]


class ProductionResource(SyncAPIResource):
    @cached_property
    def metrics(self) -> MetricsResource:
        return MetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ProductionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return ProductionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProductionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return ProductionResourceWithStreamingResponse(self)


class AsyncProductionResource(AsyncAPIResource):
    @cached_property
    def metrics(self) -> AsyncMetricsResource:
        return AsyncMetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProductionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProductionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProductionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return AsyncProductionResourceWithStreamingResponse(self)


class ProductionResourceWithRawResponse:
    def __init__(self, production: ProductionResource) -> None:
        self._production = production

    @cached_property
    def metrics(self) -> MetricsResourceWithRawResponse:
        return MetricsResourceWithRawResponse(self._production.metrics)


class AsyncProductionResourceWithRawResponse:
    def __init__(self, production: AsyncProductionResource) -> None:
        self._production = production

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithRawResponse:
        return AsyncMetricsResourceWithRawResponse(self._production.metrics)


class ProductionResourceWithStreamingResponse:
    def __init__(self, production: ProductionResource) -> None:
        self._production = production

    @cached_property
    def metrics(self) -> MetricsResourceWithStreamingResponse:
        return MetricsResourceWithStreamingResponse(self._production.metrics)


class AsyncProductionResourceWithStreamingResponse:
    def __init__(self, production: AsyncProductionResource) -> None:
        self._production = production

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithStreamingResponse:
        return AsyncMetricsResourceWithStreamingResponse(self._production.metrics)
