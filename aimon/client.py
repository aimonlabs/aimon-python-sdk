from .utils.http import get_request, post_request, post_form_request
from .utils import AIMON_SDK_BACKEND_URL
from .utils.retry import retry, RetryableError
from .models import MLModel, Application
from .dataset import Dataset, DatasetCollection
from .evaluation import Evaluation, Run
from .simple_client import SimpleAimonRelyClient
from .metrics_config import Config
from typing import List, Dict, Any
import requests


class InvalidAPIKeyError(Exception):
    pass

# An Enum for the different stages of an application
class ApplicationStage:
    PRODUCTION = "production"
    EVALUATION = "evaluation"

class Client(object):

    DETECTION_API_URL = "https://api.aimon.ai/v2/inference"

    def __init__(self, api_key, email):
        self.api_key = api_key
        self.check_api_key()
        self.user = self.get_user(email)
        self._inline_client = SimpleAimonRelyClient(api_key)

    def get_user(self, email):
        headers = self.create_auth_header()
        user = get_request('{}/v1/user'.format(AIMON_SDK_BACKEND_URL, email), headers=headers,
                           params={'email': email})
        if not user:
            raise Exception("Invalid user email specified. Please reach out to the Aimon team for help.")
        return user

    def check_api_key(self):
        # Check if the API key is approved by making an HTTP request to the Aimon UI Backend API
        res = get_request('{}/v1/api-key/{}/validate'.format(AIMON_SDK_BACKEND_URL, self.api_key))
        if 'company_id' not in res or not res['company_id']:
            raise InvalidAPIKeyError(
                "Invalid API key specified. Please contact us on discord or through info@eimon.ai for help.")

    def create_auth_header(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def create_header(self):
        headers = {}
        headers.update(self.create_auth_header())
        headers['Content-Type'] = 'application/json'
        return headers

    def list_model_types(self):
        """
        Lists all the model types available in the Aimon SDK
        """
        headers = self.create_auth_header()
        return get_request('{}/v1/list-model-types'.format(AIMON_SDK_BACKEND_URL), headers=headers)

    def model(self, name, model_type, description=None, metadata=None):
        """
        Gets or creates an ML model object.
        :param name: The name of the model
        :param model_type: The type of the model
        :param description: The description of the model
        :param metadata: The metadata associated with the model
        """
        headers = self.create_header()
        data = {
            "name": name,
            "type": model_type,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        ml_model = post_request('{}/v1/model'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=data)
        if not ml_model:
            raise Exception("Error creating mode with name {} and type {}".format(name, model_type))
        return MLModel(ml_model['company_id'], ml_model['name'], ml_model['type'], ml_model['description'],
                       ml_model['metadata_'])

    def application(self, name, model, stage, app_type, metadata=None):
        """
        Gets or creates an Application object.
        :param name: The name of the model
        :param model: An MLModel object
        :param stage: The stage of the application. Should be either "production" or "evaluation"
        :param app_type: The type of the application
        :param metadata: The metadata associated with the model
        """
        headers = self.create_header()
        if stage.lower() not in ['production', 'evaluation']:
            raise Exception("Invalid stage specified. Should be either 'production' or 'evaluation'")
        data = {
            "name": name,
            "model_name": model.name,
            "stage": stage,
            "type": app_type,
            "user_id": self.user["id"],
        }
        if metadata:
            data["metadata"] = metadata
        application = post_request('{}/v1/application'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=data)
        if not application:
            raise Exception("Error creating or retrieving the application with name {} and type {}".format(name, type))
        return Application(application['id'], application['company_id'], application['name'], application['model_id'],
                           application['stage'], application['type'], application['user_id'], application['version'],
                           application['metadata_'])

    def analyze(self, application, dataset_record, model_output, eval_run=None):
        """
        Analyzes the dataset record and model output offline.
        :param application: An Application object
        :param dataset_record: The dataset record
        :param model_output: The model output
        :param eval_run: The evaluation run
        """
        headers = self.create_header()
        data = {
            "application_id": application.app_id,
            "version": application.version,
            "prompt": dataset_record.prompt,
            "user_query": dataset_record.user_query,
            "context_docs": dataset_record.context_docs,
            "output": model_output,
        }
        if eval_run:
            data["evaluation_id"] = eval_run.evaluation_id
            data["evaluation_run_id"] = eval_run.id
        return post_request('{}/v1/save-compute-metrics'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=[data])

    @retry(RetryableError)
    def detect(self, data_to_send: List[Dict[str, Any]], config=Config()):
        """
        A synchronous API to detect quality metrics in the response of a language model.
        :param data_to_send: An array of dict objects where each dict contains a "context", a "generated_text" and
                             optionally a "config" object
        :param config: The detector configuration that will be applied to every single request.

        :return: A JSON object containing the following fields (if applicable):
                "hallucination": Indicates whether the response consisted of intrinsic or extrinsic hallucinations.
                    "is_hallucinated": top level string indicating if hallucinated or not,
                    "score": A score indicating the probability that the whole "generated_text" is hallucinated
                    "sentences": An array of objects where each object contains a sentence level hallucination "score" and
                                 the "text" of the sentence.
                "quality_metrics": A collection of quality metrics for the response of the LLM
                    "results": A dict containing results of response quality detectors like conciseness and completeness
                        "conciseness": This detector checks whether or not the response had un-necessary information
                                       for the given query and the context documents
                            "reasoning": An explanation of the score that was provided.
                            "score": A probability score of how concise the response is for the user query and context documents.
                        "completeness": This detector checks whether or not the response was complete enough for the
                                        given query and context documents
                            "reasoning": An explanation of the score that was provided.
                            "score": A probability score of how complete the response is for the user query and context documents.
                "toxicity": Indicates whether there was toxic content in the response. It uses 6 different label types for this.
                    "identity_hate": The response contained hateful content that calls out real or perceived "identity factors" of an individual or a group.
                    "insult": The response contained insulting content.
                    "obscene": The response contained lewd or disgusting words.
                    "threat": The response contained comments that threatened an individual or a group.
                    "severe_toxic", "toxic": The response did not fall into the above 4 labels but is still considered
                                             either severely toxic or generally toxic content.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        payload = []
        for item in data_to_send:
            if 'config' not in item:
                item['config'] = config.detectors
            payload.append(item)
        response = requests.post(self.DETECTION_API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code in [503, 504]:
            raise RetryableError("Status code: {} received".format(response.status_code))
        if response.status_code == 401:
            raise InvalidAPIKeyError("Use a valid Aimon API key. Request it at info@aimon.ai or on Discord.")
        if response.status_code != 200:
            raise Exception(f"Error, bad response: {response}")
        if len(response.json()) == 0 or 'error' in response.json() or 'error' in response.json()[0]:
            raise Exception(
                f"Received an error in the response: {response if len(response.json()) == 0 else response.json()}")
        return response.json()

    def get_dataset(self, name):
        headers = self.create_auth_header()
        # Check if dataset exists
        dataset = get_request('{}/v1/dataset'.format(AIMON_SDK_BACKEND_URL), headers=headers,
                              params={'name': name})
        if not dataset:
            raise Exception("Dataset with name {} not found".format(name))
        return Dataset(self.api_key, dataset['name'], dataset['description'], dataset['creation_time'], dataset['last_updated_time'],
                       dataset['sha'], dataset['user_id'])

    def create_dataset(self, name, file_path, description):
        """
        Gets or creates a Dataset object with the specified name
        """
        headers = self.create_auth_header()
        # Check if dataset exists
        dataset = get_request('{}/v1/dataset'.format(AIMON_SDK_BACKEND_URL), headers=headers,
                              params={'name': name})
        if dataset:
            return Dataset(self.api_key, dataset['name'], dataset['description'], dataset['creation_time'],
                           dataset['last_updated_time'], dataset['sha'], dataset['user_id'])

        # Dataset does not exist, create a new one
        if not file_path:
            raise Exception("file_path is required to create a new dataset")

        if not description:
            raise Exception("The description field is required to create a new dataset")

        data = {
            "name": name,
            "description": description,
            "user_id": self.user["id"]
        }

        res_ds = post_form_request('{}/v1/dataset'.format(AIMON_SDK_BACKEND_URL), file_path_to_upload=file_path,
                                 headers=headers, data=data)
        return Dataset(self.api_key, res_ds['name'], res_ds['description'], res_ds['creation_time'], res_ds['last_updated_time'],
                        res_ds['sha'], res_ds['user_id'])

    def dataset_collection(self, name, datasets, description=None):
        """
        Gets or creates a DatasetCollection object with the specified datasets
        """
        headers = self.create_auth_header()
        ds_ids = [dataset.sha for dataset in datasets]
        data = {
            "name": name,
            "user_id": self.user["id"],
            "dataset_ids": ds_ids
        }
        if description:
            data["description"] = description
        ds_coll = post_request('{}/v1/dataset-collection'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=data)
        return DatasetCollection(ds_coll['id'], ds_coll['name'], ds_coll['user_id'], datasets, ds_coll['description'])

    def evaluation(self, name, application, dataset_collection, description=None):
        """
        Gets or creates an Evaluation object with the specified name
        """
        headers = self.create_auth_header()
        data = {
            "name": name,
            "dataset_collection_id": dataset_collection.id,
            "model_id": application.model_id,
            "application_id": application.app_id,
        }
        if description:
            data["description"] = description
        eval_res = post_request('{}/v1/evaluation'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=data)
        return Evaluation(eval_res['id'], eval_res['name'], eval_res['application_id'],
                          eval_res['dataset_collection_id'], eval_res['start_time'], eval_res['description'] if 'description' in eval_res else None)



    def new_run(self, evaluation, metrics_config, tags):
        """
        Creates a new evaluation run
        """
        headers = self.create_auth_header()
        data = {
            "evaluation_id": evaluation.id,
            "metrics_config": metrics_config,
            "tags": tags,
        }
        run_res = post_request('{}/v1/evaluation-run'.format(AIMON_SDK_BACKEND_URL), headers=headers, data=data)
        return Run(run_res['id'], run_res['evaluation_id'],
                   run_res['run_number'], run_res['creation_time'], run_res['completed_time'], run_res['metadata_'])
