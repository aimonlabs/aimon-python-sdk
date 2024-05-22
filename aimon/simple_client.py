from typing import List, Dict, Any
import requests
from .utils import InvalidAPIKeyError
from .utils.retry import retry, RetryableError
from .utils import deprecated_class

from .metrics_config import Config


@deprecated_class
class SimpleAimonRelyClient(object):
    """
    DEPRECATED: This class will be removed in a future release. Use the `Client` class instead.

    A simple client that sends requests to the Aimon Rely Hallucination Detection API.
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
                             optionally a "user_query" and "config" object
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
        return response.json()
