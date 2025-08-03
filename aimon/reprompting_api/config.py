import os
from typing import Optional
from dataclasses import dataclass
import random
import string

def generate_random_string(length: int) -> str:
  """Generates a random string of letters and digits."""
  if not isinstance(length, int) or length <= 0:
      raise ValueError("Length must be a positive integer.")
  characters = string.ascii_letters + string.digits
  return ''.join(random.choice(characters) for i in range(length))

class StopReasons:
    ALL_INSTRUCTIONS_ADHERED = "all_instructions_adhered"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    CONTINUE = "instructions_failed_continue_reprompting" 
    CONTINUE_TOXICITY = "toxicity_detect_continue_reprompting"
    
    ## limits
    LATENCY_LIMIT_EXCEEDED = "latency_limit_exceeded"
    
    ##errors
    REPROMPTING_FAILED = "reprompting_failed"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class RepromptingConfig:
    """
    Configuration for the automated re-prompting pipeline.

    Attributes:
        publish (bool): Whether to publish results to app.aimon.ai.
        max_iterations (int): Maximum number of re-prompting iterations (1 initial + N retries).
        aimon_api_key (Optional[str]): API key for AIMon integration. Defaults to "AIMON_API_KEY" env var.
        model_name (Optional[str]): Model identifier for telemetry. Defaults to "aimon-react-model-{rand}".
        application_name (Optional[str]): Application identifier for telemetry. Defaults to "aimon-react-application-{rand}".
        return_telemetry (bool): Whether to include per-iteration telemetry in the response.
        return_aimon_summary (bool): Whether to include a human-readable caption summarizing re-prompting. (e.g.: 2 iterations, 0 failed instructions)
        latency_limit_ms (Optional[int]): Maximum cumulative latency (ms) before aborting. None = no limit.
        user_model_max_retries (Optional[int]): Max retries for user model calls. Defaults to 2.
        feedback_model_max_retries (Optional[int]): Max retries for feedback model calls. Defaults to 2.
    """
    publish: bool = False
    max_iterations: int = 2
    if max_iterations < 1:
        raise ValueError("Max iterations must be greater than 0")
    aimon_api_key: Optional[str] = os.getenv("AIMON_API_KEY") or "default_api_key"
    if aimon_api_key == "default_api_key":
        raise ValueError("AIMON_API_KEY environment variable is not set and no fallback value is provided.")
    model_name: Optional[str] = "aimon-react-model-" + generate_random_string(5)
    application_name: Optional[str] = "aimon-react-application-" + generate_random_string(5)
    return_telemetry: bool = False
    return_aimon_summary: bool = False
    latency_limit_ms: Optional[int] = None
    user_model_max_retries: Optional[int] = 2
    feedback_model_max_retries: Optional[int] = 2
    
    