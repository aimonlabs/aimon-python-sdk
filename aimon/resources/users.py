# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ..types import user_create_params, user_retrieve_params
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
from ..types.user import User
from .._base_client import make_request_options
from ..types.user_validate_response import UserValidateResponse

__all__ = ["UsersResource", "AsyncUsersResource"]


class UsersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsersResourceWithRawResponse:
        return UsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsersResourceWithStreamingResponse:
        return UsersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        id: str,
        email: str,
        phone: str,
        username: str,
        auth0_id: str | NotGiven = NOT_GIVEN,
        bio: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        date_joined: Union[str, datetime] | NotGiven = NOT_GIVEN,
        first_name: str | NotGiven = NOT_GIVEN,
        is_active: bool | NotGiven = NOT_GIVEN,
        is_staff: bool | NotGiven = NOT_GIVEN,
        is_superuser: bool | NotGiven = NOT_GIVEN,
        last_login: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_name: str | NotGiven = NOT_GIVEN,
        user_status: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Create a new user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/user",
            body=maybe_transform(
                {
                    "id": id,
                    "email": email,
                    "phone": phone,
                    "username": username,
                    "auth0_id": auth0_id,
                    "bio": bio,
                    "company_id": company_id,
                    "date_joined": date_joined,
                    "first_name": first_name,
                    "is_active": is_active,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                    "last_login": last_login,
                    "last_name": last_name,
                    "user_status": user_status,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )

    def retrieve(
        self,
        *,
        email: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Get user details by email

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/user",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"email": email}, user_retrieve_params.UserRetrieveParams),
            ),
            cast_to=User,
        )

    def validate(
        self,
        api_key: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserValidateResponse:
        """
        Validate API key

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key:
            raise ValueError(f"Expected a non-empty value for `api_key` but received {api_key!r}")
        return self._get(
            f"/v1/api-key/{api_key}/validate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserValidateResponse,
        )


class AsyncUsersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsersResourceWithRawResponse:
        return AsyncUsersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsersResourceWithStreamingResponse:
        return AsyncUsersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        id: str,
        email: str,
        phone: str,
        username: str,
        auth0_id: str | NotGiven = NOT_GIVEN,
        bio: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        date_joined: Union[str, datetime] | NotGiven = NOT_GIVEN,
        first_name: str | NotGiven = NOT_GIVEN,
        is_active: bool | NotGiven = NOT_GIVEN,
        is_staff: bool | NotGiven = NOT_GIVEN,
        is_superuser: bool | NotGiven = NOT_GIVEN,
        last_login: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_name: str | NotGiven = NOT_GIVEN,
        user_status: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Create a new user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/user",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "email": email,
                    "phone": phone,
                    "username": username,
                    "auth0_id": auth0_id,
                    "bio": bio,
                    "company_id": company_id,
                    "date_joined": date_joined,
                    "first_name": first_name,
                    "is_active": is_active,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                    "last_login": last_login,
                    "last_name": last_name,
                    "user_status": user_status,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=User,
        )

    async def retrieve(
        self,
        *,
        email: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> User:
        """
        Get user details by email

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/user",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"email": email}, user_retrieve_params.UserRetrieveParams),
            ),
            cast_to=User,
        )

    async def validate(
        self,
        api_key: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserValidateResponse:
        """
        Validate API key

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not api_key:
            raise ValueError(f"Expected a non-empty value for `api_key` but received {api_key!r}")
        return await self._get(
            f"/v1/api-key/{api_key}/validate",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserValidateResponse,
        )


class UsersResourceWithRawResponse:
    def __init__(self, users: UsersResource) -> None:
        self._users = users

        self.create = to_raw_response_wrapper(
            users.create,
        )
        self.retrieve = to_raw_response_wrapper(
            users.retrieve,
        )
        self.validate = to_raw_response_wrapper(
            users.validate,
        )


class AsyncUsersResourceWithRawResponse:
    def __init__(self, users: AsyncUsersResource) -> None:
        self._users = users

        self.create = async_to_raw_response_wrapper(
            users.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            users.retrieve,
        )
        self.validate = async_to_raw_response_wrapper(
            users.validate,
        )


class UsersResourceWithStreamingResponse:
    def __init__(self, users: UsersResource) -> None:
        self._users = users

        self.create = to_streamed_response_wrapper(
            users.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            users.retrieve,
        )
        self.validate = to_streamed_response_wrapper(
            users.validate,
        )


class AsyncUsersResourceWithStreamingResponse:
    def __init__(self, users: AsyncUsersResource) -> None:
        self._users = users

        self.create = async_to_streamed_response_wrapper(
            users.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            users.retrieve,
        )
        self.validate = async_to_streamed_response_wrapper(
            users.validate,
        )
