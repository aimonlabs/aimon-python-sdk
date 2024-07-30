from functools import wraps

from .common import AimonClientSingleton


class Detect:
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, values_returned, api_key=None, config=None):
        """
        :param values_returned: A list of values in the order returned by the decorated function
                                Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'
        """
        self.client = AimonClientSingleton.get_instance(api_key)
        self.config = config if config else self.DEFAULT_CONFIG
        self.values_returned = values_returned
        if self.values_returned is None or len(self.values_returned) == 0:
            raise ValueError("Values returned by the decorated function must be specified")
        if "generated_text" not in self.values_returned:
            raise ValueError("values_returned must contain 'generated_text'")
        if "context" not in self.values_returned:
            raise ValueError("values_returned must contain 'context'")

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Handle the case where the result is a single value
            if not isinstance(result, tuple):
                result = (result,)

            # Create a dictionary mapping output names to results
            result_dict = {name: value for name, value in zip(self.values_returned, result)}

            aimon_payload = {}
            if 'generated_text' in result_dict:
                aimon_payload['generated_text'] = result_dict['generated_text']
            else:
                raise ValueError("Result of the wrapped function must contain 'generated_text'")
            if 'context' in result_dict:
                aimon_payload['context'] = result_dict['context']
            else:
                raise ValueError("Result of the wrapped function must contain 'context'")
            if 'user_query' in result_dict:
                aimon_payload['user_query'] = result_dict['user_query']
            if 'instructions' in result_dict:
                aimon_payload['instructions'] = result_dict['instructions']
            aimon_payload['config'] = self.config

            data_to_send = [aimon_payload]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result + (aimon_response,)

        return wrapper
