from functools import wraps

from .common import AimonClientSingleton


class Application:
    def __init__(self, name, stage="evaluation", type="text", metadata={}):
        self.name = name
        self.stage = stage
        self.type = type
        self.metadata = metadata


class Model:
    def __init__(self, name, model_type, metadata={}):
        self.name = name
        self.model_type = model_type
        self.metadata = metadata

class DetectResult:
    def __init__(self, status, publish_response, detect_response=[]):
        self.status = status
        self.detect_response = detect_response
        self.publish_response = publish_response

class Detect:
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, values_returned, api_key=None, config=None, async_mode=False, application_name=None, model_name=None):
        """
        :param values_returned: A list of values in the order returned by the decorated function
                                Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'
        :param api_key: The API key to use for the Aimon client
        :param config: A dictionary of configuration options for the detector
        :param async_mode: Boolean, if True, the detect() function will return immediately with a DetectResult object. Default is False.
                           When True, an application and model must be provided.
        :param application_name: The name of the application to use for async_mode
        :param model_name: The name of the model to use for async_mode
        """
        self.client = AimonClientSingleton.get_instance(api_key)
        self.config = config if config else self.DEFAULT_CONFIG
        self.values_returned = values_returned
        if self.values_returned is None or len(self.values_returned) == 0:
            raise ValueError("values_returned by the decorated function must be specified")
        if "context" not in self.values_returned:
            raise ValueError("values_returned must contain 'context'")
        self.async_mode = async_mode
        if self.async_mode:
            if application_name is None:
                raise ValueError("Application name must be provided if publish is True")
            if model_name is None:
                raise ValueError("Model name must be provided if publish is True")
            self.application = Application(application_name)
            self.model = Model(model_name, "text")
            self._initialize_application_model()
        
    def _initialize_application_model(self):
        # Create or retrieve the model
        self._am_model = self.client.models.create(
            name=self.model.name,
            type=self.model.model_type,
            description="This model is named {} and is of type {}".format(self.model.name, self.model.model_type),
            metadata=self.model.metadata
        )

        # Create or retrieve the application
        self._am_app = self.client.applications.create(
            name=self.application.name,
            model_name=self._am_model.name,
            stage=self.application.stage,
            type=self.application.type,
            metadata=self.application.metadata
        )

    def _call_analyze(self, result_dict):
        if "generated_text" not in result_dict:
            raise ValueError("Result of the wrapped function must contain 'generated_text'")
        if "context" not in result_dict:
            raise ValueError("Result of the wrapped function must contain 'context'")
        _context = result_dict['context'] if isinstance(result_dict['context'], list) else [result_dict['context']]
        aimon_payload = {
            "application_id": self._am_app.id,
            "version": self._am_app.version,
            "output": result_dict['generated_text'],
            "context_docs": _context,
            "user_query": result_dict["user_query"] if 'user_query' in result_dict else "No User Query Specified",
            "prompt": result_dict['prompt'] if 'prompt' in result_dict else "No Prompt Specified",
        }
        if 'instructions' in result_dict:
            aimon_payload['instructions'] = result_dict['instructions']
        if 'actual_request_timestamp' in result_dict:
            aimon_payload["actual_request_timestamp"] = result_dict['actual_request_timestamp']

        aimon_payload['config'] = self.config
        analyze_response = self.client.analyze.create(body=[aimon_payload])
        return analyze_response
    

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

            if self.async_mode:
                analyze_res = self._call_analyze(result_dict)
                return result + (DetectResult(analyze_res.status, analyze_res),)
            else:
                aimon_response = self.client.inference.detect(body=data_to_send)[0]
                analyze_res = self._call_analyze(result_dict)
                return result + (DetectResult(max(aimon_response.status, analyze_res.status), analyze_res, aimon_response),)

        return wrapper
