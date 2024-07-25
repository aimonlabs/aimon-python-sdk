from functools import wraps

from .common import AimonClientSingleton


class DetectWithQueryFuncReturningContext(object):
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, api_key=None, config=None):
        self.client = AimonClientSingleton.get_instance(api_key)
        self.config = config if config else self.DEFAULT_CONFIG

    def __call__(self, func):
        @wraps(func)
        def wrapper(user_query, *args, **kwargs):
            result, context = func(user_query, *args, **kwargs)

            if result is None or context is None:
                raise ValueError("Result and context must be returned by the decorated function")

            data_to_send = [{
                "user_query": user_query,
                "context": context,
                "generated_text": result,
                "config": self.config
            }]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result, context, aimon_response

        return wrapper


class DetectWithQueryInstructionsFuncReturningContext(DetectWithQueryFuncReturningContext):
    def __call__(self, func):
        @wraps(func)
        def wrapper(user_query, instructions, *args, **kwargs):
            result, context = func(user_query, instructions, *args, **kwargs)

            if result is None or context is None:
                raise ValueError("Result and context must be returned by the decorated function")

            data_to_send = [{
                "user_query": user_query,
                "context": context,
                "generated_text": result,
                "instructions": instructions,
                "config": self.config
            }]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result, context, aimon_response

        return wrapper


# Another class but does not include instructions in the wrapper call
class DetectWithContextQuery(object):
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, api_key=None, config=None):
        self.client = AimonClientSingleton.get_instance(api_key)
        self.config = config if config else self.DEFAULT_CONFIG

    def __call__(self, func):
        @wraps(func)
        def wrapper(context, user_query, *args, **kwargs):
            result = func(context, user_query, *args, **kwargs)

            if result is None:
                raise ValueError("Result must be returned by the decorated function")

            data_to_send = [{
                "context": context,
                "user_query": user_query,
                "generated_text": result,
                "config": self.config
            }]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result, aimon_response

        return wrapper


class DetectWithContextQueryInstructions(DetectWithContextQuery):
    def __call__(self, func):
        @wraps(func)
        def wrapper(context, user_query, instructions, *args, **kwargs):
            result = func(context, user_query, instructions, *args, **kwargs)

            if result is None:
                raise ValueError("Result must be returned by the decorated function")

            data_to_send = [{
                "context": context,
                "user_query": user_query,
                "generated_text": result,
                "instructions": instructions,
                "config": self.config
            }]

            aimon_response = self.client.inference.detect(body=data_to_send)[0]
            return result, aimon_response

        return wrapper

