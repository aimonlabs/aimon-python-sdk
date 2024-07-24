# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import resources, _exceptions
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
from ._utils import (
    is_given,
    get_async_library,
)
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "resources", "Client", "AsyncClient"]


class Client(SyncAPIClient):
    users: resources.UsersResource
    models: resources.ModelsResource
    applications: resources.ApplicationsResource
    datasets: resources.DatasetsResource
    evaluations: resources.EvaluationsResource
    analyze: resources.AnalyzeResource
    inference: resources.InferenceResource
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
        """Construct a new synchronous client client instance."""
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

        self.users = resources.UsersResource(self)
        self.models = resources.ModelsResource(self)
        self.applications = resources.ApplicationsResource(self)
        self.datasets = resources.DatasetsResource(self)
        self.evaluations = resources.EvaluationsResource(self)
        self.analyze = resources.AnalyzeResource(self)
        self.inference = resources.InferenceResource(self)
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
    users: resources.AsyncUsersResource
    models: resources.AsyncModelsResource
    applications: resources.AsyncApplicationsResource
    datasets: resources.AsyncDatasetsResource
    evaluations: resources.AsyncEvaluationsResource
    analyze: resources.AsyncAnalyzeResource
    inference: resources.AsyncInferenceResource
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
        """Construct a new async client client instance."""
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

        self.users = resources.AsyncUsersResource(self)
        self.models = resources.AsyncModelsResource(self)
        self.applications = resources.AsyncApplicationsResource(self)
        self.datasets = resources.AsyncDatasetsResource(self)
        self.evaluations = resources.AsyncEvaluationsResource(self)
        self.analyze = resources.AsyncAnalyzeResource(self)
        self.inference = resources.AsyncInferenceResource(self)
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
        self.users = resources.UsersResourceWithRawResponse(client.users)
        self.models = resources.ModelsResourceWithRawResponse(client.models)
        self.applications = resources.ApplicationsResourceWithRawResponse(client.applications)
        self.datasets = resources.DatasetsResourceWithRawResponse(client.datasets)
        self.evaluations = resources.EvaluationsResourceWithRawResponse(client.evaluations)
        self.analyze = resources.AnalyzeResourceWithRawResponse(client.analyze)
        self.inference = resources.InferenceResourceWithRawResponse(client.inference)


class AsyncClientWithRawResponse:
    def __init__(self, client: AsyncClient) -> None:
        self.users = resources.AsyncUsersResourceWithRawResponse(client.users)
        self.models = resources.AsyncModelsResourceWithRawResponse(client.models)
        self.applications = resources.AsyncApplicationsResourceWithRawResponse(client.applications)
        self.datasets = resources.AsyncDatasetsResourceWithRawResponse(client.datasets)
        self.evaluations = resources.AsyncEvaluationsResourceWithRawResponse(client.evaluations)
        self.analyze = resources.AsyncAnalyzeResourceWithRawResponse(client.analyze)
        self.inference = resources.AsyncInferenceResourceWithRawResponse(client.inference)


class ClientWithStreamedResponse:
    def __init__(self, client: Client) -> None:
        self.users = resources.UsersResourceWithStreamingResponse(client.users)
        self.models = resources.ModelsResourceWithStreamingResponse(client.models)
        self.applications = resources.ApplicationsResourceWithStreamingResponse(client.applications)
        self.datasets = resources.DatasetsResourceWithStreamingResponse(client.datasets)
        self.evaluations = resources.EvaluationsResourceWithStreamingResponse(client.evaluations)
        self.analyze = resources.AnalyzeResourceWithStreamingResponse(client.analyze)
        self.inference = resources.InferenceResourceWithStreamingResponse(client.inference)


class AsyncClientWithStreamedResponse:
    def __init__(self, client: AsyncClient) -> None:
        self.users = resources.AsyncUsersResourceWithStreamingResponse(client.users)
        self.models = resources.AsyncModelsResourceWithStreamingResponse(client.models)
        self.applications = resources.AsyncApplicationsResourceWithStreamingResponse(client.applications)
        self.datasets = resources.AsyncDatasetsResourceWithStreamingResponse(client.datasets)
        self.evaluations = resources.AsyncEvaluationsResourceWithStreamingResponse(client.evaluations)
        self.analyze = resources.AsyncAnalyzeResourceWithStreamingResponse(client.analyze)
        self.inference = resources.AsyncInferenceResourceWithStreamingResponse(client.inference)


Client = Client

AsyncClient = AsyncClient
