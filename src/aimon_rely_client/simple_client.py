from functools import wraps
import logging
from typing import Callable, Type, Union, Tuple, Optional, List, Dict, Any
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


class Config:
    SUPPORTED_DETECTORS = {'hallucination': 'default', 'toxicity': 'default', 'conciseness': 'default',
                           'completeness': 'default'}
    SUPPORTED_VALUES = {'default'}

    def __init__(self, detectors: Dict[str, str] = None):
        """
        A Config object for detectors to be used in the Aimon API.

        :param detectors: A dictionary containing names of detectors and the kind of detector to use.
        """
        detectors_enabled = {}
        if detectors is None or len(detectors) == 0:
            detectors_enabled = {'hallucination': 'default'}
        else:
            for key, value in detectors.items():
                if value not in self.SUPPORTED_VALUES:
                    raise Exception(
                        "Value {} not supported, please contact the Aimon team on info@aimon.ai or on Discord for help".format(
                            value))
                if key in self.SUPPORTED_DETECTORS:
                    detectors_enabled[key] = value
        self.detectors = {}
        for key, value in detectors_enabled.items():
            self.detectors[key] = {'detector_name': value}


class SimpleAimonRelyClient(object):
    """
    A simple client that
    """
    URL = "https://api.aimon.ai/v2/inference"
    DEFAULT_CONFIG = Config()

    def __init__(self, api_key: str, config: Config = DEFAULT_CONFIG):
        """
        :param api_key: the Aimon Rely API key. If you don't have one, request one by sending an email to info@aimon.ai
        :param config: The detector configuration that will be applied to every single request.
        """
        if len(api_key) == 0 or "YOUR API KEY" in api_key:
            raise InvalidAPIKeyError("Enter a valid Aimon API key. Request it at info@aimon.ai or on Discord.")
        self.api_key = api_key
        self.config = config

    @retry(RetryableError)
    def detect(self, data_to_send: List[Dict[str, Any]]):
        """
        Sends an HTTP POST request to the Aimon Rely Hallucination Detection API
        :param data_to_send: An array of dict objects where each dict contains a "context", a "generated_text" and
                             optionally a "config" object
        :return: A JSON object containing the following fields (if applicable):
                "hallucination": Indicates whether the response consisted of intrinsic or extrinsic hallucinations.
                    "is_hallucinated": top level string indicating if hallucinated or not,
                    "score": A score indicating the probability that the whole "generated_text" is hallucinated
                    "sentences": An array of objects where each object contains a sentence level hallucination "score" and
                                 the "text" of the sentence.
                "quality_metrics": A collection of quality metrics for the response of the LLM
                    "results": A dict containing results of response quality detectors like conciseness and completeness
                        "conciseness": This detector checks whether or not the response had un-necessary information
                                       for the given query and the context documents
                            "reasoning": An explanation of the score that was provided.
                            "score": A probability score of how concise the response is for the user query and context documents.
                        "completeness": This detector checks whether or not the response was complete enough for the
                                        given query and context documents
                            "reasoning": An explanation of the score that was provided.
                            "score": A probability score of how complete the response is for the user query and context documents.
                "toxicity": Indicates whether there was toxic content in the response. It uses 6 different label types for this.
                    "identity_hate": The response contained hateful content that calls out real or perceived "identity factors" of an individual or a group.
                    "insult": The response contained insulting content.
                    "obscene": The response contained lewd or disgusting words.
                    "threat": The response contained comments that threatened an individual or a group.
                    "severe_toxic", "toxic": The response did not fall into the above 4 labels but is still considered
                                             either severely toxic or generally toxic content.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        payload = []
        for item in data_to_send:
            if 'config' not in item:
                item['config'] = self.config.detectors
            payload.append(item)
        response = requests.post(self.URL, json=payload, headers=headers, timeout=30)
        if response.status_code in [503, 504]:
            raise RetryableError("Status code: {} received".format(response.status_code))
        if response.status_code == 401:
            raise InvalidAPIKeyError("Use a valid Aimon API key. Request it at info@aimon.ai or on Discord.")
        if response.status_code != 200:
            raise Exception(f"Error, bad response: {response}")
        if len(response.json()) == 0 or 'error' in response.json() or 'error' in response.json()[0]:
            raise Exception(
                f"Received an error in the response: {response if len(response.json()) == 0 else response.json()}")
        return response.json()[0]
