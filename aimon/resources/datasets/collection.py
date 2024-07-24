# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
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
from ...types.datasets import collection_create_params, collection_retrieve_params
from ...types.datasets.collection_create_response import CollectionCreateResponse
from ...types.datasets.collection_retrieve_response import CollectionRetrieveResponse

__all__ = ["CollectionResource", "AsyncCollectionResource"]


class CollectionResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CollectionResourceWithRawResponse:
        return CollectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CollectionResourceWithStreamingResponse:
        return CollectionResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        dataset_ids: List[str],
        name: str,
        id: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        creation_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        last_updated_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CollectionCreateResponse:
        """
        Create a new dataset collection

        Args:
          dataset_ids: A list of dataset IDs included in this collection.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/dataset-collection",
            body=maybe_transform(
                {
                    "dataset_ids": dataset_ids,
                    "name": name,
                    "id": id,
                    "company_id": company_id,
                    "creation_time": creation_time,
                    "description": description,
                    "last_updated_time": last_updated_time,
                    "user_id": user_id,
                },
                collection_create_params.CollectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CollectionCreateResponse,
        )

    def retrieve(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CollectionRetrieveResponse:
        """
        Retrieve a dataset collection by name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/dataset-collection",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"name": name}, collection_retrieve_params.CollectionRetrieveParams),
            ),
            cast_to=CollectionRetrieveResponse,
        )


class AsyncCollectionResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCollectionResourceWithRawResponse:
        return AsyncCollectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCollectionResourceWithStreamingResponse:
        return AsyncCollectionResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        dataset_ids: List[str],
        name: str,
        id: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        creation_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        last_updated_time: Union[str, datetime] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CollectionCreateResponse:
        """
        Create a new dataset collection

        Args:
          dataset_ids: A list of dataset IDs included in this collection.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/dataset-collection",
            body=await async_maybe_transform(
                {
                    "dataset_ids": dataset_ids,
                    "name": name,
                    "id": id,
                    "company_id": company_id,
                    "creation_time": creation_time,
                    "description": description,
                    "last_updated_time": last_updated_time,
                    "user_id": user_id,
                },
                collection_create_params.CollectionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CollectionCreateResponse,
        )

    async def retrieve(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CollectionRetrieveResponse:
        """
        Retrieve a dataset collection by name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/dataset-collection",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"name": name}, collection_retrieve_params.CollectionRetrieveParams),
            ),
            cast_to=CollectionRetrieveResponse,
        )


class CollectionResourceWithRawResponse:
    def __init__(self, collection: CollectionResource) -> None:
        self._collection = collection

        self.create = to_raw_response_wrapper(
            collection.create,
        )
        self.retrieve = to_raw_response_wrapper(
            collection.retrieve,
        )


class AsyncCollectionResourceWithRawResponse:
    def __init__(self, collection: AsyncCollectionResource) -> None:
        self._collection = collection

        self.create = async_to_raw_response_wrapper(
            collection.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            collection.retrieve,
        )


class CollectionResourceWithStreamingResponse:
    def __init__(self, collection: CollectionResource) -> None:
        self._collection = collection

        self.create = to_streamed_response_wrapper(
            collection.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            collection.retrieve,
        )


class AsyncCollectionResourceWithStreamingResponse:
    def __init__(self, collection: AsyncCollectionResource) -> None:
        self._collection = collection

        self.create = async_to_streamed_response_wrapper(
            collection.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            collection.retrieve,
        )
