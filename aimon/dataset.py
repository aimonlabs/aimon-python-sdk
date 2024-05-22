from .utils.http import get_request
from .utils import AIMON_SDK_BACKEND_URL

class Dataset(object):
    def __init__(self, api_key, name, description, creation_time, last_updated_time, sha, user_id):
        self.api_key = api_key
        self.name = name
        self.description = description
        self.creation_time = creation_time
        self.last_updated_time = last_updated_time
        self.sha = sha
        self.user_id = user_id

    def records(self):
        res = self.get_raw_records_json()
        # Call the dataset API to get the dataset and return a list of DatasetRecord objects
        dataset_records = [DatasetRecord(r['prompt'], r['user_query'], r['context_docs']) for r in res]
        return dataset_records

    def get_raw_records_json(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        return get_request("{}/v1/dataset-records".format(AIMON_SDK_BACKEND_URL), headers=headers,
                          params={'sha': self.sha})

    def __str__(self):
        return f"Dataset(name={self.name}, description={self.description}, creation_time={self.creation_time}, last_updated_time={self.last_updated_time}, sha={self.sha}, user_id={self.user_id})"

    def __repr__(self):
        return self.__str__()


class DatasetCollection(object):
    def __init__(self, ds_id, name, user_id, datasets, description=None):
        self.id = ds_id
        self.name = name
        self.user_id = user_id
        self.datasets = datasets
        self.description = description

    def records(self):
        records = []
        for dataset in self.datasets:
            records.extend(dataset.records())
        return records

    def __iter__(self):
        # Return an iterator for the datasets in the collection
        return iter(self.datasets)

    def __str__(self):
        return f"DatasetCollection(id={self.id}, name={self.name}, user_id={self.user_id}, datasets={self.datasets}, description={self.description})"

    def __repr__(self):
        return self.__str__()

class DatasetRecord(object):

    def __init__(self, prompt, user_query, context_docs):
        self.prompt = prompt
        self.user_query = user_query
        self.context_docs = context_docs

    def __str__(self):
        return f"DatasetRecord(prompt={self.prompt}, user_query={self.user_query}, context_docs={self.context_docs})"

    def __repr__(self):
        return self.__str__()

