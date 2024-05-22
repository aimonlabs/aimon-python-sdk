import warnings
import functools

AIMON_SDK_BACKEND_URL = "https://pbe-api.aimon.ai"

class InvalidAPIKeyError(Exception):
    def __init__(self):
        super().__init__("Invalid API Key")

def deprecated_class(cls):
    """
    This decorator can be used to mark classes as deprecated.
    It will result in a warning being emitted when the class is instantiated.
    """
    orig_init = cls.__init__

    @functools.wraps(orig_init)
    def new_init(self, *args, **kwargs):
        warnings.warn(
            f"{cls.__name__} is deprecated and will be removed in a future version.",
            category=DeprecationWarning,
            stacklevel=2
        )
        orig_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls
