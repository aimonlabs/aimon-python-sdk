class Dataset(object):
    def __init__(self, name, description, creation_time, last_updated_time, s3_location, sha, user_id):
        self.name = name
        self.description = description
        self.creation_time = creation_time
        self.last_updated_time = last_updated_time
        self.s3_location = s3_location
        self.sha = sha
        self.user_id = user_id

    def to_pandas(self):
        import boto3
        import pandas as pd
        # Load the dataset from the S3 location and return a pandas dataframe
        s3_client = boto3.client('s3')
        # parse s3_location string to get bucket and key. Example: "s3://bucket/path/to/file.csv"
        s3_location = self.s3_location
        bucket = self.s3_location.replace("s3://", "").split("/")[0]
        key  = self.s3_location.replace(f"s3://{bucket}/", "")
        print("Bucket: {}, key: {}".format(bucket, key))
        file = s3_client.get_object(Bucket=bucket, Key=key)
        return pd.read_json(file['Body'])

    def records(self):
        import boto3
        import json
        import pandas as pd
        # Load the dataset from the S3 location and return a pandas dataframe
        s3_client = boto3.client('s3')
        # parse s3_location string to get bucket and key. Example: "s3://bucket/path/to/file.csv"
        s3_location = self.s3_location
        bucket = self.s3_location.replace("s3://", "").split("/")[0]
        key = self.s3_location.replace(f"s3://{bucket}/", "")
        print("Bucket: {}, key: {}".format(bucket, key))
        file = s3_client.get_object(Bucket=bucket, Key=key)
        json_records = json.loads(file['Body'].read())
        dataset_records = [DatasetRecord(r['prompt'], r['user_query'], r['context_docs']) for r in json_records]
        return dataset_records

    def __str__(self):
        return f"Dataset(name={self.name}, description={self.description}, creation_time={self.creation_time}, last_updated_time={self.last_updated_time}, s3_location={self.s3_location}, sha={self.sha}, user_id={self.user_id})"

    def __repr__(self):
        return self.__str__()

class DatasetCollection(object):
    def __init__(self, ds_id, name, user_id, datasets, description=None):
        self.id = ds_id
        self.name = name
        self.user_id = user_id
        self.datasets = datasets
        self.description = description

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

