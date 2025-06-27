from functools import wraps
import os

import json, textwrap

from aimon import Client
from .evaluate import Application, Model

class DetectResult:
    """
    A class to represent the result of an AIMon detection operation.

    This class encapsulates the status of the detection operation, the response from the detection service,
    and optionally, the response from publishing the result to the AIMon UI.

    Attributes:
    -----------
    status : int
        The HTTP status code of the detection operation.
    detect_response : object
        The response object from the AIMon synchronous detection.
    publish_response : list, optional
        The response from publishing the result to the AIMon UI, if applicable. This is also
        populated when the detect operation is run in async mode.

    Methods:
    --------
    __str__()
        Returns a string representation of the DetectResult object.
    __repr__()
        Returns a string representation of the DetectResult object (same as __str__).
    """

    def __init__(self, status, detect_response, publish=None):
        self.status = status
        self.detect_response = detect_response
        self.publish_response = publish if publish is not None else []

    def __str__(self):
        return (
            f"DetectResult(\n"
            f"  status={self.status},\n"
            f"  detect_response={self._format_response_item(self.detect_response)},\n"
            f"  publish_response={self.publish_response}\n"
            f")"
        )

    def __repr__(self):
        return str(self)
    
    def _format_response_item(self, response_item, wrap_limit=100):
        formatted_items = []
        response_item = (
            response_item.to_dict() if hasattr(response_item, 'to_dict') else response_item
        )
        for key, value in response_item.items():
            # Convert value to a JSON string with indentation
            json_str = json.dumps(value, indent=4)
            
            # Wrap the JSON string to the specified character limit
            wrapped_str = "\n".join(
                textwrap.fill(line, width=wrap_limit) for line in json_str.splitlines()
            )
            
            formatted_items.append(f"{key}: {wrapped_str}")
        
        return "\n".join(formatted_items)

class Detect:
    """
    A decorator class for detecting various qualities in LLM-generated text using AIMon's detection services.

    This decorator wraps a function that generates text using an LLM and sends the generated text
    along with context to AIMon for analysis. It can be used in both synchronous and asynchronous modes,
    and optionally publishes results to the AIMon UI.

    Parameters:
    -----------
    values_returned : list
        A list of values in the order returned by the decorated function.
        Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'.
    api_key : str, optional
        The API key to use for the AIMon client. If not provided, it will attempt to use the AIMON_API_KEY environment variable.
    config : dict, optional
        A dictionary of configuration options for the detector. Defaults to {'hallucination': {'detector_name': 'default'}}.
    async_mode : bool, optional
        If True, the detect() function will return immediately with a DetectResult object. Default is False.
    publish : bool, optional
        If True, the payload will be published to AIMon and can be viewed on the AIMon UI. Default is False.
    application_name : str, optional
        The name of the application to use when publish is True.
    model_name : str, optional
        The name of the model to use when publish is True.
    must_compute : str, optional
        Indicates the computation strategy. Must be either 'all_or_none' or 'ignore_failures'. Default is 'all_or_none'.

    Example:
    --------
    >>> from aimon.decorators import Detect
    >>> import os
    >>> 
    >>> # Configure the detector
    >>> detect = Detect(
    ...     values_returned=['context', 'generated_text', 'user_query'],
    ...     api_key=os.getenv('AIMON_API_KEY'),
    ...     config={
    ...         'hallucination': {'detector_name': 'default'},
    ...         'toxicity': {'detector_name': 'default'}
    ...     },
    ...     publish=True,
    ...     application_name='my_summarization_app',
    ...     model_name='gpt-3.5-turbo'
    ... )
    >>> 
    >>> # Define a simple lambda function to simulate an LLM
    >>> your_llm_function = lambda context, query: f"Summary of '{context}' based on query: {query}"
    >>> 
    >>> # Use the decorator on your LLM function
    >>> @detect
    ... def generate_summary(context, query):
    ...     summary = your_llm_function(context, query)
    ...     return context, summary, query
    >>> 
    >>> # Use the decorated function
    >>> context = "The quick brown fox jumps over the lazy dog."
    >>> query = "Summarize the given text."
    >>> context, summary, query, aimon_result = generate_summary(context, query)
    >>> 
    >>> # Print the generated summary
    >>> print(f"Generated summary: {summary}")
    >>> 
    >>> # Check the AIMon detection results
    >>> print(f"Hallucination score: {aimon_result.detect_response.hallucination['score']}")
    >>> print(f"Toxicity score: {aimon_result.detect_response.toxicity['score']}")
    """
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, values_returned, api_key=None, config=None, async_mode=False, publish=False, application_name=None, model_name=None, must_compute='all_or_none'):
        """
        :param values_returned: A list of values in the order returned by the decorated function
                                Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'
        :param api_key: The API key to use for the AIMon client
        :param config: A dictionary of configuration options for the detector
        :param async_mode: Boolean, if True, the detect() function will return immediately with a DetectResult object. Default is False.
                           The payload will also be published to AIMon and can be viewed on the AIMon UI.
        :param publish: Boolean, if True, the payload will be published to AIMon and can be viewed on the AIMon UI. Default is False.
        :param application_name: The name of the application to use when publish is True
        :param model_name: The name of the model to use when publish is True
        :param must_compute: String, indicates the computation strategy. Must be either 'all_or_none' or 'ignore_failures'. Default is 'all_or_none'.
        """
        api_key = os.getenv('AIMON_API_KEY') if not api_key else api_key
        if api_key is None:
            raise ValueError("API key is None")
        self.client = Client(auth_header="Bearer {}".format(api_key))
        self.config = config if config else self.DEFAULT_CONFIG
        self.values_returned = values_returned
        if self.values_returned is None or not hasattr(self.values_returned, '__iter__') or len(self.values_returned) == 0:
            raise ValueError("values_returned must be specified and be an iterable")
        self.async_mode = async_mode
        self.publish = publish
        if self.async_mode:
            self.publish = True
        if self.publish:
            if application_name is None:
                raise ValueError("Application name must be provided if publish is True")
            if model_name is None:
                raise ValueError("Model name must be provided if publish is True")    

        # Validate must_compute parameter
        if not isinstance(must_compute, str):
            raise ValueError("`must_compute` must be a string value")
        if must_compute not in ['all_or_none', 'ignore_failures']:
            raise ValueError("`must_compute` must be either 'all_or_none' or 'ignore_failures'")
        self.must_compute = must_compute

        self.application_name = application_name
        self.model_name = model_name

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Handle the case where the result is a single value
            if not isinstance(result, tuple):
                result = (result,)

            # Create a dictionary mapping output names to results
            aimon_payload = {name: value for name, value in zip(self.values_returned, result)}

            aimon_payload['config'] = self.config
            aimon_payload['publish'] = self.publish
            aimon_payload['async_mode'] = self.async_mode
            aimon_payload['must_compute'] = self.must_compute

            # Include application_name and model_name if publishing
            if self.publish:
                aimon_payload['application_name'] = self.application_name
                aimon_payload['model_name'] = self.model_name

            data_to_send = [aimon_payload]

            try:
                detect_response = self.client.inference.detect(body=data_to_send)
                # Check if the response is a list
                if isinstance(detect_response, list) and len(detect_response) > 0:
                    detect_result = detect_response[0]
                elif isinstance(detect_response, dict):
                    detect_result = detect_response  # Single dict response
                else:
                    raise ValueError("Unexpected response format from detect API: {}".format(detect_response))
            except Exception as e:
                # Log the error and raise it
                print(f"Error during detection: {e}")
                raise

            # Return the original result along with the DetectResult
            return result + (DetectResult(200 if detect_result else 500, detect_result),)


        return wrapper
