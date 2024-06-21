from typing import Dict
import json

class Config:
    SUPPORTED_DETECTORS = {'hallucination': 'default', 'toxicity': 'default', 'conciseness': 'default',
                           'completeness': 'default'}
    SUPPORTED_VALUES = {'default', 'hall_v2'}

    def __init__(self, detectors: Dict[str, str] = None):
        """
        A Config object for detectors to be used in the Aimon API.

        :param detectors: A dictionary containing names of detectors and the kind of detector to use.
        """
        detectors_enabled = {}
        if detectors is None or len(detectors) == 0:
            detectors_enabled = {'hallucination': 'default'}
        else:
            for key, value in detectors.items():
                if value not in self.SUPPORTED_VALUES:
                    raise Exception(
                        "Value {} not supported, please contact the Aimon team on info@aimon.ai or on Discord for help".format(
                            value))
                if key in self.SUPPORTED_DETECTORS:
                    detectors_enabled[key] = value
        self.detectors = {}
        for key, value in detectors_enabled.items():
            self.detectors[key] = {'detector_name': value}

    def to_json(self):
        # Convert the Config object to a JSON object
        return json.dumps(self.detectors)


