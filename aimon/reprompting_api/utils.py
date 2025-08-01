"""
utils.py — Utility functions for processing AIMon reprompting detector results.

This module provides helper functions for:
- Extracting failed instructions across instruction adherence, groundedness, and toxicity detectors.
- Calculating a residual error score (0–1) for evaluating LLM responses.

These utilities are primarily used by the RepromptingPipeline to:
- Build telemetry.
- Select best iterations.
- Guide corrective re-prompting logic.

Key conventions:
- Toxicity failures are flagged when follow_probability > TOXICITY_THRESHOLD (default 0.25).
- Residual error scoring penalizes low follow probabilities more heavily and adds a flat penalty for any toxicity failures.
"""
from typing import Callable, Type, Union, Tuple, Optional, List
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

# toxicity threshold for AIMon detection; Follow probabilities above this are considered failures
TOXICITY_THRESHOLD = 0.25

def _count_toxicity_failures(result) -> int:
    """
    Count the number of toxicity instructions whose follow probability exceeds the threshold.

    Args:
        result: AIMon detection result containing a `toxicity` section.

    Returns:
        int: Number of failed toxicity instructions.
    """
    return sum(
        1
        for inst in result.detect_response.toxicity.get("instructions_list", [])
        if inst.get("follow_probability", 0.0) > TOXICITY_THRESHOLD
    )

def toxicity_check(result) -> bool:
    """
    Check whether any toxicity instructions exceed the threshold.

    Args:
        result: AIMon detection result containing a `toxicity` section.

    Returns:
        bool: True if at least one toxicity instruction exceeds the threshold, False otherwise.
    """
    return _count_toxicity_failures(result) > 0


def get_failed_toxicity_instructions(result) -> List[dict]:
    """
    Extract failed toxicity instructions exceeding the threshold.

    Args:
        result: AIMon detection result containing a `toxicity` section.

    Returns:
        List[dict]: A list of dictionaries, each describing a failed toxicity instruction with:
            - type (str): "toxicity_failure"
            - source (str): "toxicity"
            - instruction (str): The instruction text.
            - score (float): The follow probability.
            - explanation (str): The explanation for the failure.
    """
    failed = []
    for inst in result.detect_response.toxicity.get("instructions_list", []):
        if inst.get("follow_probability", 0.0) > TOXICITY_THRESHOLD:
            failed.append({
                "type": "toxicity_failure",
                "source": "toxicity",
                "instruction": inst.get("instruction", ""),
                "score": inst.get("follow_probability", 0.0),
                "explanation": inst.get("explanation", "")
            })
    return failed
    
def get_failed_instructions(result) -> List[dict]:
    """
    Extract all failed instructions from adherence, groundedness, and toxicity detectors.

    Args:
        result: AIMon detection result containing `instruction_adherence`, `groundedness`, and `toxicity` sections.

    Returns:
        List[dict]: A list of failed instructions with:
            - type (str): Failure type ("instruction_adherence_failure", "groundedness_failure", "toxicity_failure").
            - source (str): Detector source ("instruction_adherence", "groundedness", "toxicity").
            - instruction (str): The instruction text.
            - score (float): Follow probability.
            - explanation (str): Explanation for the failure.
    """
    failed = []
    # Adherence & groundedness
    for source in ["instruction_adherence", "groundedness"]:
        for inst in getattr(result.detect_response, source, {}).get("instructions_list", []):
            if not inst.get("label", True):
                failed.append({
                    "type": f"{source}_failure",
                    "source": source,
                    "instruction": inst.get("instruction", ""),
                    "score": inst.get("follow_probability", 0.0),
                    "explanation": inst.get("explanation", "")
                })
    # Sort by score (most confident first)
    failed.sort(key=lambda x: x["score"], reverse=True)
    return failed

def get_failed_instructions_count(result) -> int:
    """
    Count all failed instructions across adherence, groundedness, and toxicity.

    Args:
        result: AIMon detection result containing `instruction_adherence`, `groundedness`, and `toxicity` sections.

    Returns:
        int: Total number of failed instructions.
    """
    count = 0
    # Instruction adherence
    for inst in result.detect_response.instruction_adherence.get("instructions_list", []):
        if not inst.get("label", True):
            count += 1
    # Groundedness
    for inst in result.detect_response.groundedness.get("instructions_list", []):
        if not inst.get("label", True):
            count += 1
    count += _count_toxicity_failures(result)  # Toxicity
    return count

def get_residual_error_score(result):
    """
    Compute a normalized residual error score (0–1) based on:
    - Groundedness follow probabilities
    - Instruction adherence follow probabilities
    - Toxicity (inverted: 1 - follow_probability)

    Logic:
    1. Collect follow probabilities for groundedness & adherence.
    2. For toxicity, use 1 - follow_probability (since high follow = low error).
    3. Compute a penalized average using the helper.
    4. Clamp the final score to [0,1].
    """
    combined_probs = []

    for source in ["groundedness", "instruction_adherence"]:
        combined_probs.extend([
            item["follow_probability"]
            for item in getattr(result.detect_response, source, {}).get("instructions_list", [])
        ])

    # For toxicity, invert the follow probability
    combined_probs.extend([
        1 - item["follow_probability"]
        for item in getattr(result.detect_response, "toxicity", {}).get("instructions_list", [])
    ])

    residual_error_score = penalized_average(combined_probs) if combined_probs else 0.0
    residual_error_score = min(1.0, max(0.0, residual_error_score))
    return round(residual_error_score, 2)


def penalized_average(probs: List[float]) -> float:
    """
    Compute a penalized average of follow probabilities.

    Penalizes probabilities <0.5 more heavily by doubling their penalty. 
    Probabilities > 0.5 (passed instructions) recieve no penalty

    Args:
        probs (List[float]): A list of follow probabilities. Must be non-empty.

    Returns:
        float: Penalized average. Return -1 if probs is empty.
    """
    if not probs:  # handle division by zero for empty list
        return -1
    
    penalties = []
    for p in probs:
        if p >= 0.5:
            penalty = 0
        else:
            penalty = (1 - p) * 2  # heavier penalty
        penalties.append(penalty)
    return sum(penalties) / len(penalties)