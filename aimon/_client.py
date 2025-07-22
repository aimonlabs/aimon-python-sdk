# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import users, models, analyze, metrics, inference, retrieval
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.datasets import datasets
from .resources.evaluations import evaluations
from .resources.applications import applications

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Client", "AsyncClient"]


class Client(SyncAPIClient):
    users: users.UsersResource
    models: models.ModelsResource
    applications: applications.ApplicationsResource
    datasets: datasets.DatasetsResource
    evaluations: evaluations.EvaluationsResource
    analyze: analyze.AnalyzeResource
    inference: inference.InferenceResource
    retrieval: retrieval.RetrievalResource
    metrics: metrics.MetricsResource
    with_raw_response: ClientWithRawResponse
    with_streaming_response: ClientWithStreamedResponse

    # client options
    auth_header: str

    def __init__(
        self,
        *,
        auth_header: str,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Client client instance."""
        self.auth_header = auth_header

        if base_url is None:
            base_url = os.environ.get("CLIENT_BASE_URL")
        if base_url is None:
            base_url = f"https://pbe-api.aimon.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.users = users.UsersResource(self)
        self.models = models.ModelsResource(self)
        self.applications = applications.ApplicationsResource(self)
        self.datasets = datasets.DatasetsResource(self)
        self.evaluations = evaluations.EvaluationsResource(self)
        self.analyze = analyze.AnalyzeResource(self)
        self.inference = inference.InferenceResource(self)
        self.retrieval = retrieval.RetrievalResource(self)
        self.metrics = metrics.MetricsResource(self)
        self.with_raw_response = ClientWithRawResponse(self)
        self.with_streaming_response = ClientWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        auth_header = self.auth_header
        return {"Authorization": auth_header}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        auth_header: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            auth_header=auth_header or self.auth_header,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncClient(AsyncAPIClient):
    users: users.AsyncUsersResource
    models: models.AsyncModelsResource
    applications: applications.AsyncApplicationsResource
    datasets: datasets.AsyncDatasetsResource
    evaluations: evaluations.AsyncEvaluationsResource
    analyze: analyze.AsyncAnalyzeResource
    inference: inference.AsyncInferenceResource
    retrieval: retrieval.AsyncRetrievalResource
    metrics: metrics.AsyncMetricsResource
    with_raw_response: AsyncClientWithRawResponse
    with_streaming_response: AsyncClientWithStreamedResponse

    # client options
    auth_header: str

    def __init__(
        self,
        *,
        auth_header: str,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncClient client instance."""
        self.auth_header = auth_header

        if base_url is None:
            base_url = os.environ.get("CLIENT_BASE_URL")
        if base_url is None:
            base_url = f"https://pbe-api.aimon.ai"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.users = users.AsyncUsersResource(self)
        self.models = models.AsyncModelsResource(self)
        self.applications = applications.AsyncApplicationsResource(self)
        self.datasets = datasets.AsyncDatasetsResource(self)
        self.evaluations = evaluations.AsyncEvaluationsResource(self)
        self.analyze = analyze.AsyncAnalyzeResource(self)
        self.inference = inference.AsyncInferenceResource(self)
        self.retrieval = retrieval.AsyncRetrievalResource(self)
        self.metrics = metrics.AsyncMetricsResource(self)
        self.with_raw_response = AsyncClientWithRawResponse(self)
        self.with_streaming_response = AsyncClientWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        auth_header = self.auth_header
        return {"Authorization": auth_header}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        auth_header: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            auth_header=auth_header or self.auth_header,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class ClientWithRawResponse:
    def __init__(self, client: Client) -> None:
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.models = models.ModelsResourceWithRawResponse(client.models)
        self.applications = applications.ApplicationsResourceWithRawResponse(client.applications)
        self.datasets = datasets.DatasetsResourceWithRawResponse(client.datasets)
        self.evaluations = evaluations.EvaluationsResourceWithRawResponse(client.evaluations)
        self.analyze = analyze.AnalyzeResourceWithRawResponse(client.analyze)
        self.inference = inference.InferenceResourceWithRawResponse(client.inference)
        self.retrieval = retrieval.RetrievalResourceWithRawResponse(client.retrieval)
        self.metrics = metrics.MetricsResourceWithRawResponse(client.metrics)


class AsyncClientWithRawResponse:
    def __init__(self, client: AsyncClient) -> None:
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.models = models.AsyncModelsResourceWithRawResponse(client.models)
        self.applications = applications.AsyncApplicationsResourceWithRawResponse(client.applications)
        self.datasets = datasets.AsyncDatasetsResourceWithRawResponse(client.datasets)
        self.evaluations = evaluations.AsyncEvaluationsResourceWithRawResponse(client.evaluations)
        self.analyze = analyze.AsyncAnalyzeResourceWithRawResponse(client.analyze)
        self.inference = inference.AsyncInferenceResourceWithRawResponse(client.inference)
        self.retrieval = retrieval.AsyncRetrievalResourceWithRawResponse(client.retrieval)
        self.metrics = metrics.AsyncMetricsResourceWithRawResponse(client.metrics)


class ClientWithStreamedResponse:
    def __init__(self, client: Client) -> None:
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.models = models.ModelsResourceWithStreamingResponse(client.models)
        self.applications = applications.ApplicationsResourceWithStreamingResponse(client.applications)
        self.datasets = datasets.DatasetsResourceWithStreamingResponse(client.datasets)
        self.evaluations = evaluations.EvaluationsResourceWithStreamingResponse(client.evaluations)
        self.analyze = analyze.AnalyzeResourceWithStreamingResponse(client.analyze)
        self.inference = inference.InferenceResourceWithStreamingResponse(client.inference)
        self.retrieval = retrieval.RetrievalResourceWithStreamingResponse(client.retrieval)
        self.metrics = metrics.MetricsResourceWithStreamingResponse(client.metrics)


class AsyncClientWithStreamedResponse:
    def __init__(self, client: AsyncClient) -> None:
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.models = models.AsyncModelsResourceWithStreamingResponse(client.models)
        self.applications = applications.AsyncApplicationsResourceWithStreamingResponse(client.applications)
        self.datasets = datasets.AsyncDatasetsResourceWithStreamingResponse(client.datasets)
        self.evaluations = evaluations.AsyncEvaluationsResourceWithStreamingResponse(client.evaluations)
        self.analyze = analyze.AsyncAnalyzeResourceWithStreamingResponse(client.analyze)
        self.inference = inference.AsyncInferenceResourceWithStreamingResponse(client.inference)
        self.retrieval = retrieval.AsyncRetrievalResourceWithStreamingResponse(client.retrieval)
        self.metrics = metrics.AsyncMetricsResourceWithStreamingResponse(client.metrics)


Client = Client

AsyncClient = AsyncClient
