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


class Analyze(object):
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, application, model, api_key=None, evaluation_name=None, dataset_collection_name=None, eval_tags=None, instructions=None, config=None):
        self.client = AimonClientSingleton.get_instance(api_key)
        self.application = application
        self.model = model
        self.evaluation_name = evaluation_name
        self.dataset_collection_name = dataset_collection_name
        self.eval_tags = eval_tags
        self.instructions = instructions
        self.config = config if config else self.DEFAULT_CONFIG
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

        if self.evaluation_name is not None:

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
            result = func(record['context_docs'], record['user_query'], *args, **kwargs)
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

    def _run_production_analysis(self, func, context, sys_prompt, user_query, args, kwargs):
        result = func(context, sys_prompt, user_query, *args, **kwargs)
        if result is None:
            raise ValueError("Result must be returned by the decorated function")
        payload = {
            "application_id": self._am_app.id,
            "version": self._am_app.version,
            "prompt": sys_prompt or "",
            "user_query": user_query or "",
            "context_docs": context or [],
            "output": result
        }
        aimon_response = self.client.analyze.create(body=[payload])
        return aimon_response, result

    def __call__(self, func):
        @wraps(func)
        def wrapper(context=None, sys_prompt=None, user_query=None, *args, **kwargs):

            if self.evaluation_name is not None:
                return self._run_eval(func, args, kwargs)
            else:
                # Production mode, run the provided args through the user function
                return self._run_production_analysis(func, context, sys_prompt, user_query, args, kwargs)

        return wrapper


analyze = Analyze
