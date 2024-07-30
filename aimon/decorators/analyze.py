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


class AnalyzeBase:

    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, application, model, api_key=None):
        """
        :param application: An Application object
        :param model: A Model object
        :param api_key: The API key to use for the Aimon client
        """
        self.client = AimonClientSingleton.get_instance(api_key)
        self.application = application
        self.model = model
        self.initialize()

    def initialize(self):
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


class AnalyzeEval(AnalyzeBase):

    def __init__(self, application, model, evaluation_name, dataset_collection_name,
                 api_key=None, eval_tags=None, config=None):
        """
        The wrapped function should have a signature as follows:

            def func(context_docs, user_query, prompt, *args, **kwargs):
                # Your code here
                return output
        The first argument must be a context_docs which is of type List[str]
        The second argument must be a user_query which is of type str
        The third argument must be a prompt which is of type str

        :param application: An Application object
        :param model: A Model object
        :param evaluation_name: The name of the evaluation
        :param dataset_collection_name: The name of the dataset collection
        :param api_key: The API key to use for the AIMon client
        :param eval_tags: A list of tags to associate with the evaluation
        :param config: A dictionary containing the AIMon configuration for the evaluation


        """
        super().__init__(application, model, api_key)
        self.evaluation_name = evaluation_name
        self.dataset_collection_name = dataset_collection_name
        self.eval_tags = eval_tags
        self.config = config if config else self.DEFAULT_CONFIG
        self.eval_initialize()

    def eval_initialize(self):
        if self.dataset_collection_name is None:
            raise ValueError("Dataset collection name must be provided for running an evaluation.")

        # Create or retrieve the dataset collection
        self._am_dataset_collection = self.client.datasets.collection.retrieve(name=self.dataset_collection_name)

        # Create or retrieve the evaluation
        self._eval = self.client.evaluations.create(
            name=self.evaluation_name,
            application_id=self._am_app.id,
            model_id=self._am_model.id,
            dataset_collection_id=self._am_dataset_collection.id
        )

    def _run_eval(self, func, args, kwargs):
        # Create an evaluation run
        eval_run = self.client.evaluations.run.create(
            evaluation_id=self._eval.id,
            metrics_config=self.config,
        )
        # Get all records from the datasets
        dataset_collection_records = []
        for dataset_id in self._am_dataset_collection.dataset_ids:
            dataset_records = self.client.datasets.records.list(sha=dataset_id)
            dataset_collection_records.extend(dataset_records)
        results = []
        for record in dataset_collection_records:
            result = func(record["context_docs"], record["user_query"], record["prompt"], *args, **kwargs)

            # TODO: Add instructions and config to the payload once supported
            payload = {
                "application_id": self._am_app.id,
                "version": self._am_app.version,
                "prompt": record['prompt'] or "",
                "user_query": record['user_query'] or "",
                "context_docs": [d for d in record['context_docs']],
                "output": result,
                "evaluation_id": self._eval.id,
                "evaluation_run_id": eval_run.id,
            }
            results.append((result, self.client.analyze.create(body=[payload])))
        return results

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._run_eval(func, args, kwargs)
        return wrapper


class AnalyzeProd(AnalyzeBase):

    def __init__(self, application, model, values_returned, api_key=None, instructions=None, config=None):
        """
        The wrapped function should return a tuple of values in the order specified by values_returned. In addition,
        the wrapped function should accept a parameter named eval_obj which will be used when using this decorator
        in evaluation mode.

        :param application: An Application object
        :param model: A Model object
        :param values_returned: A list of values in the order returned by the decorated function
                                Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'
        """

        super().__init__(application, model, api_key)
        self.instructions = instructions
        self.values_returned = values_returned
        if self.values_returned is None or len(self.values_returned) == 0:
            raise ValueError("Values returned by the decorated function must be specified")
        if "generated_text" not in self.values_returned:
            raise ValueError("values_returned must contain 'generated_text'")
        if "context" not in self.values_returned:
            raise ValueError("values_returned must contain 'context'")
        self.config = config if config else self.DEFAULT_CONFIG

    def _run_production_analysis(self, func, args, kwargs):
        result = func(*args, **kwargs)
        if result is None:
            raise ValueError("Result must be returned by the decorated function")
        # Handle the case where the result is a single value
        if not isinstance(result, tuple):
            result = (result,)

        # Create a dictionary mapping output names to results
        result_dict = {name: value for name, value in zip(self.values_returned, result)}

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
            "prompt": result_dict['prompt'] if 'prompt' in result_dict else "No Prompt Specified"
        }
        # TODO: Add instructions and config to the payload once supported
        # if 'instructions' in result_dict:
        #     aimon_payload['instructions'] = result_dict['instructions']
        # aimon_payload['config'] = self.config
        aimon_response = self.client.analyze.create(body=[aimon_payload])
        return result + (aimon_response,)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Production mode, run the provided args through the user function
            return self._run_production_analysis(func, args, kwargs)

        return wrapper
