from functools import wraps
import logging
from typing import Callable, Type, Union, Tuple, Optional, List, Dict
import random
import time
import requests

def retry(
    exception_to_check: Union[Type[BaseException], Tuple[Type[BaseException], ...]],
    tries: int = 5,
    delay: int = 3,
    backoff: int = 2,
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.WARNING,
    re_raise: bool = True,
    jitter: float = 0.1
) -> Callable:
    """
    Retry calling the decorated function using an exponential backoff.

    :param exception_to_check: Exception or a tuple of exceptions to check.
    :param tries: Number of times to try (not retry) before giving up.
    :param delay: Initial delay between retries in seconds.
    :param backoff: Backoff multiplier e.g., a value of 2 will double the delay each retry.
    :param logger: Logger to use. If None, print.
    :param log_level: Logging level.
    :param re_raise: Whether to re-raise the exception after the last retry.
    :param jitter: The maximum jitter to apply to the delay as a fraction of the delay.
    """
    def deco_retry(func: Callable) -> Callable:
        @wraps(func)
        def f_retry(*args, **kwargs):
            remaining_tries, current_delay = tries, delay
            while remaining_tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    msg = f"{e}, Retrying in {current_delay} seconds..."
                    if logger:
                        logger.log(log_level, msg)
                    else:
                        print(msg)
                    time.sleep(current_delay * (1 + jitter * (2 * random.random() - 1)))
                    remaining_tries -= 1
                    current_delay *= backoff

            try:
                return func(*args, **kwargs)
            except exception_to_check as e:
                msg = f"Failed after {tries} tries. {e}"
                if logger:
                    logger.log(log_level, msg)
                else:
                    print(msg)
                if re_raise:
                    raise

        return f_retry
    return deco_retry

class RetryableError(Exception):
    pass

class InvalidAPIKeyError(Exception):
    pass

class SimpleAimonRelyClient(object):
    """
    A simple client that
    """
    URL = "https://api.aimon.ai/v1/inference"

    def __init__(self, api_key: str):
        """
        :param api_key: the Aimon Rely API key. If you don't have one, request one by sending an email to info@aimon.ai
        """
        if len(api_key) == 0 or "YOUR API KEY" in api_key:
            raise InvalidAPIKeyError("Enter a valid Aimon API key. Request it at info@aimon.ai or on Discord.")
        self.api_key = api_key

    @retry(RetryableError)
    def detect(self, data_to_send: List[Dict[str, str]]):
        """
        Sends an HTTP POST request to the Aimon Rely Hallucination Detection API
        :param data_to_send: An array of dict objects where each dict contains a "context" and "generated_text"
        :return: A JSON object containing the following fields:
                    "is_hallucinated": top level string indicating if hallucinated or not,
                    "score": A score indicating the probability that the whole "generated_text" is hallucinated
                    "sentences": An array of objects where each object contains a sentence level hallucination "score" and
                                 the "text" of the sentence.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        response = requests.post(self.URL, json=data_to_send, headers=headers, timeout=30)
        if response.status_code in [503, 504]:
            raise RetryableError("Status code: {} received".format(response.status_code))
        if response.status_code == 401:
            raise InvalidAPIKeyError("Use a valid Aimon API key. Request it at info@aimon.ai or on Discord.")
        if response.status_code != 200:
            raise Exception(f"Error, bad response: {response}")
        if len(response.json()) == 0 or 'error' in response.json() or 'error' in response.json()[0]:
            raise Exception(f"Received an error in the response: {response if len(response.json()) == 0 else response.json()}")
        return response.json()[0]
