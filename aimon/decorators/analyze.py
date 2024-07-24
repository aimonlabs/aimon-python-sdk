from functools import wraps


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


class Analyze:
    DEFAULT_CONFIG = {'hallucination_v0.2': {'detector_name': 'default'}}

    def __init__(self, client, application, model, evaluation_name, dataset_collection_name, eval_tags=None, instructions=None, config=None):
        self.client = client
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
            description="This model is named {} and is of type {}".format(self.mode.name, self.model.model_type),
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

        # Create or retrieve the dataset collection
        # TODO: create this API in the SDK backend and publish the SDK
        self._am_dataset_collection = self.client.dataset_collections.retrieve(self.dataset_collection_name)

        # Create or retrieve the evaluation
        self._eval = self.client.evaluations.create(
            name=self.evaluation_name,
            application_id=self._am_app.id,
            model_id=self._am_model.id,
            dataset_collection_id=self._am_dataset_collection.id
        )

    def __call__(self, func):
        @wraps(func)
        def wrapper(context, user_query, *args, **kwargs):

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
                    "context_docs": [d.page_content for d in record['context_docs']],
                    "output": result,
                    "evaluation_id": self._eval.id,
                    "evaluation_run_id": eval_run.id,
                }
                results.append((result, self.client.analyze.create(body=[payload])))

            return results

        return wrapper


analyze = Analyze
