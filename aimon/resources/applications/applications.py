# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ...types import application_create_params, application_delete_params, application_retrieve_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from .production.production import (
    ProductionResource,
    AsyncProductionResource,
    ProductionResourceWithRawResponse,
    AsyncProductionResourceWithRawResponse,
    ProductionResourceWithStreamingResponse,
    AsyncProductionResourceWithStreamingResponse,
)
from .evaluations.evaluations import (
    EvaluationsResource,
    AsyncEvaluationsResource,
    EvaluationsResourceWithRawResponse,
    AsyncEvaluationsResourceWithRawResponse,
    EvaluationsResourceWithStreamingResponse,
    AsyncEvaluationsResourceWithStreamingResponse,
)
from ...types.application_create_response import ApplicationCreateResponse
from ...types.application_delete_response import ApplicationDeleteResponse
from ...types.application_retrieve_response import ApplicationRetrieveResponse

__all__ = ["ApplicationsResource", "AsyncApplicationsResource"]


class ApplicationsResource(SyncAPIResource):
    @cached_property
    def evaluations(self) -> EvaluationsResource:
        return EvaluationsResource(self._client)

    @cached_property
    def production(self) -> ProductionResource:
        return ProductionResource(self._client)

    @cached_property
    def with_raw_response(self) -> ApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return ApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return ApplicationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model_name: str,
        name: str,
        type: str,
        id: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        context_source_id: str | NotGiven = NOT_GIVEN,
        last_query_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        stage: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationCreateResponse:
        """
        Create a new application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/application",
            body=maybe_transform(
                {
                    "model_name": model_name,
                    "name": name,
                    "type": type,
                    "id": id,
                    "company_id": company_id,
                    "context_source_id": context_source_id,
                    "last_query_timestamp": last_query_timestamp,
                    "metadata": metadata,
                    "model_id": model_id,
                    "stage": stage,
                    "user_id": user_id,
                    "version": version,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    def retrieve(
        self,
        *,
        name: str,
        stage: str,
        type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationRetrieveResponse:
        """
        Retrieve an application by name, user_id, and version

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/application",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "name": name,
                        "stage": stage,
                        "type": type,
                    },
                    application_retrieve_params.ApplicationRetrieveParams,
                ),
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    def delete(
        self,
        *,
        name: str,
        stage: str,
        version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationDeleteResponse:
        """
        Delete an application by name, stage, and version

        Args:
          name: The name of the application to delete

          stage: The stage of the application (e.g., production, evaluation)

          version: The version of the application to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/v1/application",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "name": name,
                        "stage": stage,
                        "version": version,
                    },
                    application_delete_params.ApplicationDeleteParams,
                ),
            ),
            cast_to=ApplicationDeleteResponse,
        )


class AsyncApplicationsResource(AsyncAPIResource):
    @cached_property
    def evaluations(self) -> AsyncEvaluationsResource:
        return AsyncEvaluationsResource(self._client)

    @cached_property
    def production(self) -> AsyncProductionResource:
        return AsyncProductionResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncApplicationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return AsyncApplicationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncApplicationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return AsyncApplicationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model_name: str,
        name: str,
        type: str,
        id: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        context_source_id: str | NotGiven = NOT_GIVEN,
        last_query_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        model_id: str | NotGiven = NOT_GIVEN,
        stage: str | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationCreateResponse:
        """
        Create a new application

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/application",
            body=await async_maybe_transform(
                {
                    "model_name": model_name,
                    "name": name,
                    "type": type,
                    "id": id,
                    "company_id": company_id,
                    "context_source_id": context_source_id,
                    "last_query_timestamp": last_query_timestamp,
                    "metadata": metadata,
                    "model_id": model_id,
                    "stage": stage,
                    "user_id": user_id,
                    "version": version,
                },
                application_create_params.ApplicationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ApplicationCreateResponse,
        )

    async def retrieve(
        self,
        *,
        name: str,
        stage: str,
        type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationRetrieveResponse:
        """
        Retrieve an application by name, user_id, and version

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/application",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "name": name,
                        "stage": stage,
                        "type": type,
                    },
                    application_retrieve_params.ApplicationRetrieveParams,
                ),
            ),
            cast_to=ApplicationRetrieveResponse,
        )

    async def delete(
        self,
        *,
        name: str,
        stage: str,
        version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ApplicationDeleteResponse:
        """
        Delete an application by name, stage, and version

        Args:
          name: The name of the application to delete

          stage: The stage of the application (e.g., production, evaluation)

          version: The version of the application to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/v1/application",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "name": name,
                        "stage": stage,
                        "version": version,
                    },
                    application_delete_params.ApplicationDeleteParams,
                ),
            ),
            cast_to=ApplicationDeleteResponse,
        )


class ApplicationsResourceWithRawResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = to_raw_response_wrapper(
            applications.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            applications.delete,
        )

    @cached_property
    def evaluations(self) -> EvaluationsResourceWithRawResponse:
        return EvaluationsResourceWithRawResponse(self._applications.evaluations)

    @cached_property
    def production(self) -> ProductionResourceWithRawResponse:
        return ProductionResourceWithRawResponse(self._applications.production)


class AsyncApplicationsResourceWithRawResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_raw_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            applications.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            applications.delete,
        )

    @cached_property
    def evaluations(self) -> AsyncEvaluationsResourceWithRawResponse:
        return AsyncEvaluationsResourceWithRawResponse(self._applications.evaluations)

    @cached_property
    def production(self) -> AsyncProductionResourceWithRawResponse:
        return AsyncProductionResourceWithRawResponse(self._applications.production)


class ApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: ApplicationsResource) -> None:
        self._applications = applications

        self.create = to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            applications.delete,
        )

    @cached_property
    def evaluations(self) -> EvaluationsResourceWithStreamingResponse:
        return EvaluationsResourceWithStreamingResponse(self._applications.evaluations)

    @cached_property
    def production(self) -> ProductionResourceWithStreamingResponse:
        return ProductionResourceWithStreamingResponse(self._applications.production)


class AsyncApplicationsResourceWithStreamingResponse:
    def __init__(self, applications: AsyncApplicationsResource) -> None:
        self._applications = applications

        self.create = async_to_streamed_response_wrapper(
            applications.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            applications.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            applications.delete,
        )

    @cached_property
    def evaluations(self) -> AsyncEvaluationsResourceWithStreamingResponse:
        return AsyncEvaluationsResourceWithStreamingResponse(self._applications.evaluations)

    @cached_property
    def production(self) -> AsyncProductionResourceWithStreamingResponse:
        return AsyncProductionResourceWithStreamingResponse(self._applications.production)
