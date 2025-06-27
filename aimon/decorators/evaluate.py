from functools import wraps
from datetime import datetime
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
        evaluation_name=None,
        headers=None,
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

    # Auto-generate evaluation name if not provided
    if not evaluation_name:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        evaluation_name = f"{application_name}-{model_name}-{timestamp}"

    # Validata headers to be non-empty and contain atleast the context_docs column
    if not headers:
        raise ValueError("Headers must be a non-empty list")

    am_model = client.models.create(
        name=model.name,
        type=model.model_type,
        description="This model is named {} and is of type {}".format(model.name, model.model_type),
        metadata=model.metadata
    )

    # Create application and models
    am_app = client.applications.create(
        name=application.name,
        model_name=model.name,
        stage=application.stage,
        type=application.type,
        metadata=application.metadata
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

        # Construct the payload for the analysis
        payload = {
            **record,
            "config": config,
            "application_id": am_app.id,
            "version": am_app.version,
            "evaluation_id": am_eval.id,
            "evaluation_run_id": eval_run.id,
        }
        
        results.append(EvaluateResponse(record['output'], client.analyze.create(body=[payload])))

    return results



