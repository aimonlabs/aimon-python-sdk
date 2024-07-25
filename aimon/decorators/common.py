import os
from aimon import Client


# A singleton class that instantiates the Aimon client once
# and provides a method to get the client instance
class AimonClientSingleton:
    _instance = None

    @staticmethod
    def get_instance(api_key=None):
        if AimonClientSingleton._instance is None:
            api_key = os.getenv('AIMON_API_KEY') if not api_key else api_key
            AimonClientSingleton._instance = Client(auth_header="Bearer {}".format(api_key))
        return AimonClientSingleton._instance
