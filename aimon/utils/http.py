import json

import requests
from .retry import retry, RetryableError

@retry(RetryableError)
def get_request(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code in [503, 504]:
            raise RetryableError("Status code: {} received".format(response.status_code))
        if response.status_code in [401, 403]:
            raise Exception("Unauthorized request. Please check your API key.")
        if response.status_code != 200:
            return None
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None

@retry(RetryableError)
def post_request(url, headers=None, data=None):
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [503, 504]:
            raise RetryableError("Status code: {} received".format(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception("Error, bad response: {}".format(response))
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None

@retry(RetryableError)
def post_form_request(url, file_path_to_upload, headers=None, data=None):
    # Create a form-data request that contains a key called "file" whole value is the file content to upload,
    # This content needs to be read from the path specified by file_path_to_upload. There is also a key called "json_data"
    # that contains the JSON data to be sent along with the file.
    try:
        with open(file_path_to_upload, 'rb') as file:
            form_data = {'json_data': json.dumps(data)}
            files = {'file': file}
            response = requests.post(url, headers=headers, files=files, data=form_data)
            if response.status_code in [503, 504]:
                raise RetryableError("Status code: {} received".format(response.status_code))
            if response.status_code not in [200, 201]:
                raise Exception("Error, bad response: {}".format(response))
            return response.json()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None

