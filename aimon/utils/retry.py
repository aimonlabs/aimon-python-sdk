from typing import Callable, Type, Union, Tuple, Optional
from functools import wraps
import logging
import random
import time

def retry(
        exception_to_check: Union[Type[BaseException], Tuple[Type[BaseException], ...]],
        tries: int = 5,
        delay: int = 3,
        backoff: int = 2,
        logger: Optional[logging.Logger] = None,
        log_level: int = logging.WARNING,
        re_raise: bool = True,
        jitter: float = 0.1
) -> Callable:
    """
    Retry calling the decorated function using an exponential backoff.

    :param exception_to_check: Exception or a tuple of exceptions to check.
    :param tries: Number of times to try (not retry) before giving up.
    :param delay: Initial delay between retries in seconds.
    :param backoff: Backoff multiplier e.g., a value of 2 will double the delay each retry.
    :param logger: Logger to use. If None, print.
    :param log_level: Logging level.
    :param re_raise: Whether to re-raise the exception after the last retry.
    :param jitter: The maximum jitter to apply to the delay as a fraction of the delay.
    """

    def deco_retry(func: Callable) -> Callable:
        @wraps(func)
        def f_retry(*args, **kwargs):
            remaining_tries, current_delay = tries, delay
            while remaining_tries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    msg = f"{e}, Retrying in {current_delay} seconds..."
                    if logger:
                        logger.log(log_level, msg)
                    else:
                        print(msg)
                    time.sleep(current_delay * (1 + jitter * (2 * random.random() - 1)))
                    remaining_tries -= 1
                    current_delay *= backoff

            try:
                return func(*args, **kwargs)
            except exception_to_check as e:
                msg = f"Failed after {tries} tries. {e}"
                if logger:
                    logger.log(log_level, msg)
                else:
                    print(msg)
                if re_raise:
                    raise

        return f_retry

    return deco_retry


class RetryableError(Exception):
    pass
