from functools import wraps


class Detect:
    DEFAULT_CONFIG = {'hallucination_v0.2': {'detector_name': 'default'}}

    def __init__(self, client, instructions=None, config=None):
        self.client = client
        self.instructions = instructions
        self.config = config if config else self.DEFAULT_CONFIG

    def __call__(self, func):
        @wraps(func)
        def wrapper(context, user_query, *args, **kwargs):
            result = func(context, user_query, *args, **kwargs)

            data_to_send = [{
                "context": context,
                "user_query": user_query,
                "generated_text": result,
                "config": self.config
            }]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result, aimon_response

        return wrapper


detect = Detect
