from functools import wraps

from aimon import Client
import inspect
import warnings

class Application:
    """
    Represents an application in the Aimon system.

    This class encapsulates the properties of an application, including its name,
    stage, type, and associated metadata.

    Attributes:
    -----------
    name : str
        The name of the application.
    stage : str, optional
        The stage of the application (default is "evaluation").
    type : str, optional
        The type of the application (default is "text").
    metadata : dict, optional
        Additional metadata associated with the application (default is an empty dict).

    Example:
    --------
    >>> app = Application("my_app", stage="production", type="text", metadata={"version": "1.0"})
    >>> print(app.name)
    my_app
    """

    def __init__(self, name, stage="evaluation", type="text", metadata={}):
        """
        Initialize a new Application instance.

        Parameters:
        -----------
        name : str
            The name of the application.
        stage : str, optional
            The stage of the application (default is "evaluation").
        type : str, optional
            The type of the application (default is "text").
        metadata : dict, optional
            Additional metadata associated with the application (default is an empty dict).
        """
        self.name = name
        self.stage = stage
        self.type = type
        self.metadata = metadata


class Model:
    """
    This is a model.

    Attributes:
    -----------
    name : str
        The name of the model.
    model_type : str
        The type of the model.
    metadata : dict, optional
        Additional metadata associated with the model (default is an empty dict).

    Example:
    --------
    >>> model = Model("gpt-4", "text", metadata={"version": "1.0"})
    >>> print(model.name)
    gpt-4
    >>> print(model.model_type)
    text
    """

    def __init__(self, name, model_type, metadata={}):
        """
        Initialize a new Model instance.

        Parameters:
        -----------
        name : str
            The name of the model.
        model_type : str
            The type of the model.
        metadata : dict, optional
            Additional metadata associated with the model (default is an empty dict).
        """
        self.name = name
        self.model_type = model_type
        self.metadata = metadata

class EvaluateResponse:
    """
    Represents the response from an evaluation.

    This class encapsulates the output of the evaluated function and the response
    from the Aimon API analysis.

    Attributes:
    -----------
    output : Any
        The output of the evaluated function.
    response : Any
        The response from the Aimon API analysis.

    Methods:
    --------
    __str__() : str
        Returns a string representation of the EvaluateResponse.
    __repr__() : str
        Returns a string representation of the EvaluateResponse (same as __str__).

    Example:
    --------
    >>> output = "Generated text"
    >>> response = {"analysis": "Some analysis data"}
    >>> eval_response = EvaluateResponse(output, response)
    >>> print(eval_response)
    EvaluateResponse(output=Generated text, response={'analysis': 'Some analysis data'})
    """

    def __init__(self, output, response):
        """
        Initialize a new EvaluateResponse instance.

        Parameters:
        -----------
        output : Any
            The output of the evaluated function.
        response : Any
            The response from the Aimon API analysis.
        """
        self.output = output
        self.response = response

    def __str__(self):
        return f"EvaluateResponse(output={self.output}, response={self.response})"

    def __repr__(self):
        return str(self)


def evaluate(
        application_name,
        model_name,
        dataset_collection_name, 
        evaluation_name, 
        headers, 
        api_key=None,
        aimon_client=None,
        config=None
):
    """
    Run an evaluation on a dataset collection using the Aimon API.

    This function creates or retrieves an application, model, and dataset collection,
    then runs an evaluation on the specified dataset collection. It processes each record
    in the dataset and sends it to the Aimon API for analysis.

    Parameters:
    -----------
    application_name : str
        The name of the application to run the evaluation on.
    model_name : str
        The name of the model to run the evaluation on.
    dataset_collection_name : str
        The name of the dataset collection to run the evaluation on.
    evaluation_name : str
        The name of the evaluation to be created.
    headers : list
        A list of column names in the dataset to be used for the evaluation.
        Must include 'context_docs'.
    api_key : str, optional
        The API key to use for the Aimon client. Required if aimon_client is not provided.
    aimon_client : Client, optional
        An instance of the Aimon client to use for the evaluation. If not provided,
        a new client will be created using the api_key.
    config : dict, optional
        A dictionary of configuration options for the evaluation.

    Returns:
    --------
    list of EvaluateResponse
        A list of EvaluateResponse objects containing the output and response for each
        record in the dataset collection.

    Raises:
    -------
    ValueError
        If headers is empty or doesn't contain 'context_docs', or if required fields
        are missing from the dataset records.

    Notes:
    ------
    The dataset records must contain 'context_docs' and all fields specified in the
    'headers' argument. The 'prompt', 'output', and 'instructions' fields are optional.

    Example:
    --------
    >>> from aimon import Client
    >>> import os
    >>> headers = ["context_docs", "user_query", "output"]
    >>> config = {
    ...     "hallucination": {"detector_name": "default"},
    ...     "instruction_adherence": {"detector_name": "default"}
    ... }
    >>> results = evaluate(
    ...     application_name="my_app",
    ...     model_name="gpt-4o",
    ...     dataset_collection_name="my_dataset_collection",
    ...     evaluation_name="my_evaluation",
    ...     headers=headers,
    ...     api_key=os.getenv("AIMON_API_KEY"),
    ...     config=config
    ... )
    >>> for result in results:
    ...     print(f"Output: {result.output}")
    ...     print(f"Response: {result.response}")
    ...     print("---")
    """
    client = aimon_client if aimon_client else Client(auth_header="Bearer {}".format(api_key))
    application = Application(name=application_name, stage="evaluation")
    model = Model(name=model_name, model_type="text")

    # Validata headers to be non-empty and contain atleast the context_docs column
    if not headers:
        raise ValueError("Headers must be a non-empty list")
    if "context_docs" not in headers:
        raise ValueError("Headers must contain the column 'context_docs'")

    # Create application and models
    am_app = client.applications.create(
        name=application.name,
        model_name=model.name,
        stage=application.stage,
        type=application.type,
        metadata=application.metadata
    )

    am_model = client.models.create(
        name=model.name,
        type=model.model_type,
        description="This model is named {} and is of type {}".format(model.name, model.model_type),
        metadata=model.metadata
    )

    # Create or retrieve the dataset collection
    am_dataset_collection = client.datasets.collection.retrieve(name=dataset_collection_name)

    # Create or retrieve the evaluation
    am_eval = client.evaluations.create(
        name=evaluation_name,
        application_id=am_app.id,
        model_id=am_model.id,
        dataset_collection_id=am_dataset_collection.id
    )

    # Create an evaluation run
    eval_run = client.evaluations.run.create(
        evaluation_id=am_eval.id,
        metrics_config=config
    )

    # Get all records from the datasets
    dataset_collection_records = []
    for dataset_id in am_dataset_collection.dataset_ids:
        dataset_records = client.datasets.records.list(sha=dataset_id)
        dataset_collection_records.extend(dataset_records)

    results = []
    for record in dataset_collection_records:
        # The record must contain the context_docs and user_query fields.
        # The prompt, output and instructions fields are optional.
        # Inspect the record and call the function with the appropriate arguments
        for ag in headers:
            if ag not in record:
                raise ValueError("Dataset record must contain the column '{}' as specified in the 'headers'"
                                    " argument in the decorator".format(ag))
        
        if "context_docs" not in record:
            raise ValueError("Dataset record must contain the column 'context_docs'")

        _context = record['context_docs'] if isinstance(record['context_docs'], list) else [record['context_docs']]
        # Construct the payload for the analysis
        payload = {
            "application_id": am_app.id,
            "version": am_app.version,
            "context_docs": [d for d in _context],
            "evaluation_id": am_eval.id,
            "evaluation_run_id": eval_run.id,
        }
        if "prompt" in record and record["prompt"]:
            payload["prompt"] = record["prompt"]
        if "user_query" in record and record["user_query"]:
            payload["user_query"] = record["user_query"]
        if "output" in record and record["output"]:
            payload["output"] = record["output"]
        if "instruction_adherence" in config and "instructions" not in record:
            raise ValueError("When instruction_adherence is specified in the config, "
                             "'instructions' must be present in the dataset")
        if "instructions" in record and "instruction_adherence" in config:
            # Only pass instructions if instruction_adherence is specified in the config
            payload["instructions"] = record["instructions"] or ""
        payload["config"] = config
        results.append(EvaluateResponse(record['output'], client.analyze.create(body=[payload])))

    return results

class AnalyzeBase:
    DEFAULT_CONFIG = {'hallucination': {'detector_name': 'default'}}

    def __init__(self, application, model, api_key=None, config=None):
        """
        :param application: An Application object
        :param model: A Model object
        :param api_key: The API key to use for the Aimon client
        """
        self.client = Client(auth_header="Bearer {}".format(api_key))
        self.application = application
        self.model = model
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


class AnalyzeEval(AnalyzeBase):

    def __init__(self, application, model, evaluation_name, dataset_collection_name, headers,
                 api_key=None, eval_tags=None, config=None):
        """
        The wrapped function should have a signature as follows:
            def func(context_docs, user_query, prompt, instructions *args, **kwargs):
                # Your code here
                return output
        [Required] The first argument must be a 'context_docs' which is of type List[str].
        [Required] The second argument must be a 'user_query' which is of type str.
        [Optional] The third argument must be a 'prompt' which is of type str
        [Optional] If an 'instructions' column is present in the dataset, then the fourth argument
        must be 'instructions' which is of type str
        [Optional] If an 'output' column is present in the dataset, then the fifth argument
        must be 'output' which is of type str
        Return: The function must return an output which is of type str

        :param application: An Application object
        :param model: A Model object
        :param evaluation_name: The name of the evaluation
        :param dataset_collection_name: The name of the dataset collection
        :param headers: A list containing the headers to be used for the evaluation
        :param api_key: The API key to use for the AIMon client
        :param eval_tags: A list of tags to associate with the evaluation
        :param config: A dictionary containing the AIMon configuration for the evaluation


        """
        super().__init__(application, model, api_key, config)
        warnings.warn(
            f"{self.__class__.__name__} is deprecated and will be removed in a later release. Please use the evaluate method instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.headers = headers
        self.evaluation_name = evaluation_name
        self.dataset_collection_name = dataset_collection_name
        self.eval_tags = eval_tags
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
            # The record must contain the context_docs and user_query fields.
            # The prompt, output and instructions fields are optional.
            # Inspect the record and call the function with the appropriate arguments
            arguments = []
            for ag in self.headers:
                if ag not in record:
                    raise ValueError("Record must contain the column '{}' as specified in the 'headers'"
                                     " argument in the decorator".format(ag))
                arguments.append(record[ag])
            # Inspect the function signature to ensure that it accepts the correct arguments
            sig = inspect.signature(func)
            params = sig.parameters
            if len(params) < len(arguments):
                raise ValueError("Function must accept at least {} arguments".format(len(arguments)))
            # Ensure that the first len(arguments) parameters are named correctly
            param_names = list(params.keys())
            if param_names[:len(arguments)] != self.headers:
                raise ValueError("Function arguments must be named as specified by the 'headers' argument: {}".format(
                    self.headers))

            result = func(*arguments, *args, **kwargs)
            _context = record['context_docs'] if isinstance(record['context_docs'], list) else [record['context_docs']]
            payload = {
                "application_id": self._am_app.id,
                "version": self._am_app.version,
                "prompt": record['prompt'] or "",
                "user_query": record['user_query'] or "",
                "context_docs": [d for d in _context],
                "output": result,
                "evaluation_id": self._eval.id,
                "evaluation_run_id": eval_run.id,
            }
            if "instruction_adherence" in self.config and "instructions" not in record:
                raise ValueError("When instruction_adherence is specified in the config, "
                                 "'instructions' must be present in the dataset")
            if "instructions" in record and "instruction_adherence" in self.config:
                # Only pass instructions if instruction_adherence is specified in the config
                payload["instructions"] = record["instructions"] or ""
            payload["config"] = self.config
            results.append((result, self.client.analyze.create(body=[payload])))
        return results

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self._run_eval(func, args, kwargs)

        return wrapper
    

class AnalyzeProd(AnalyzeBase):

    def __init__(self, application, model, values_returned, api_key=None, config=None):
        """
        The wrapped function should return a tuple of values in the order specified by values_returned. In addition,
        the wrapped function should accept a parameter named eval_obj which will be used when using this decorator
        in evaluation mode.

        :param application: An Application object
        :param model: A Model object
        :param values_returned: A list of values in the order returned by the decorated function
                                Acceptable values are 'generated_text', 'context', 'user_query', 'instructions'
        """
        application.stage = "production"
        super().__init__(application, model, api_key, config)
        warnings.warn(
            f"{self.__class__.__name__} is deprecated and will be removed in a later release. Please use Detect with async=True instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.values_returned = values_returned
        if self.values_returned is None or len(self.values_returned) == 0:
            raise ValueError("Values returned by the decorated function must be specified")
        if "generated_text" not in self.values_returned:
            raise ValueError("values_returned must contain 'generated_text'")
        if "context" not in self.values_returned:
            raise ValueError("values_returned must contain 'context'")
        if "instruction_adherence" in self.config and "instructions" not in self.values_returned:
            raise ValueError(
                "When instruction_adherence is specified in the config, 'instructions' must be returned by the decorated function")
        if "instructions" in self.values_returned and "instruction_adherence" not in self.config:
            raise ValueError(
                "instruction_adherence must be specified in the config for returning 'instructions' by the decorated function")
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
            "prompt": result_dict['prompt'] if 'prompt' in result_dict else "No Prompt Specified",
        }
        if 'instructions' in result_dict:
            aimon_payload['instructions'] = result_dict['instructions']
        if 'actual_request_timestamp' in result_dict:
            aimon_payload["actual_request_timestamp"] = result_dict['actual_request_timestamp']

        aimon_payload['config'] = self.config
        aimon_response = self.client.analyze.create(body=[aimon_payload])
        return result + (aimon_response,)

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Production mode, run the provided args through the user function
            return self._run_production_analysis(func, args, kwargs)

        return wrapper



