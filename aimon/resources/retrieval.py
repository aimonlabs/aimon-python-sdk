# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ..types import retrieval_rerank_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.retrieval_rerank_response import RetrievalRerankResponse

__all__ = ["RetrievalResource", "AsyncRetrievalResource"]


class RetrievalResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RetrievalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return RetrievalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RetrievalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return RetrievalResourceWithStreamingResponse(self)

    def rerank(
        self,
        *,
        context_docs: List[str],
        queries: List[str],
        task_definition: str,
        model_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalRerankResponse:
        """
        This endpoint reranks query-context results and allows providing a task
        definition containing domain-specific relevance information. Users can provide a
        few-shot examples to fine-tune the model for better domain-specific
        understanding.

        Args:
          context_docs: List of context documents.

          queries: List of queries.

          task_definition: Description of the task to guide relevance ranking.

          model_type: Optional model type to be used for reranking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/rerank-icl",
            body=maybe_transform(
                {
                    "context_docs": context_docs,
                    "queries": queries,
                    "task_definition": task_definition,
                    "model_type": model_type,
                },
                retrieval_rerank_params.RetrievalRerankParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalRerankResponse,
        )


class AsyncRetrievalResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRetrievalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRetrievalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRetrievalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/aimonlabs-python#with_streaming_response
        """
        return AsyncRetrievalResourceWithStreamingResponse(self)

    async def rerank(
        self,
        *,
        context_docs: List[str],
        queries: List[str],
        task_definition: str,
        model_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalRerankResponse:
        """
        This endpoint reranks query-context results and allows providing a task
        definition containing domain-specific relevance information. Users can provide a
        few-shot examples to fine-tune the model for better domain-specific
        understanding.

        Args:
          context_docs: List of context documents.

          queries: List of queries.

          task_definition: Description of the task to guide relevance ranking.

          model_type: Optional model type to be used for reranking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/rerank-icl",
            body=await async_maybe_transform(
                {
                    "context_docs": context_docs,
                    "queries": queries,
                    "task_definition": task_definition,
                    "model_type": model_type,
                },
                retrieval_rerank_params.RetrievalRerankParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalRerankResponse,
        )


class RetrievalResourceWithRawResponse:
    def __init__(self, retrieval: RetrievalResource) -> None:
        self._retrieval = retrieval

        self.rerank = to_raw_response_wrapper(
            retrieval.rerank,
        )


class AsyncRetrievalResourceWithRawResponse:
    def __init__(self, retrieval: AsyncRetrievalResource) -> None:
        self._retrieval = retrieval

        self.rerank = async_to_raw_response_wrapper(
            retrieval.rerank,
        )


class RetrievalResourceWithStreamingResponse:
    def __init__(self, retrieval: RetrievalResource) -> None:
        self._retrieval = retrieval

        self.rerank = to_streamed_response_wrapper(
            retrieval.rerank,
        )


class AsyncRetrievalResourceWithStreamingResponse:
    def __init__(self, retrieval: AsyncRetrievalResource) -> None:
        self._retrieval = retrieval

        self.rerank = async_to_streamed_response_wrapper(
            retrieval.rerank,
        )
