AIMON_SDK_BACKEND_URL = "https://am-sdk-backend-ser-3357-7615d7e0-zobj9ovx.onporter.run"


class InvalidAPIKeyError(Exception):
    def __init__(self):
        super().__init__("Invalid API Key")
