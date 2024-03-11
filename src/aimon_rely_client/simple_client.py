from typing import List, Dict

import requests

from functools import wraps
def retry(ExceptionToCheck, tries=5, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        #logger.exception(msg) # would print stack trace
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

import time
import requests

class RetryableError(Exception):
    pass


class SimpleAimonRelyClient(object):
    """
    A simple client that
    """
    URL = "https://am-hd-m1-ser-2380-7615d7e0-wkx4g8t7.onporter.run/inference"

    def __init__(self, api_key: str):
        """
        :param api_key: the Aimon Rely API key. If you don't have one, request one by sending an email to info@aimon.ai
        """
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
        if response.status_code != 200:
            raise Exception(f"Error, bad response: {response}")
        if len(response.json()) == 0 or 'error' in response.json() or 'error' in response.json()[0]:
            raise Exception(f"Received an error in the response: {response if len(response.json()) == 0 else response.json()}")
        return response.json()[0]
