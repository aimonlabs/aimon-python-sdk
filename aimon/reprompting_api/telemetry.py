import json
import uuid
from datetime import datetime

class TelemetryLogger:
    """
    A lightweight logger for recording telemetry events during re-prompting pipeline execution.

    Telemetry is stored in memory for retrieval and returned by the pipeline when requested.
    """
    def __init__(self):
        """Initialize an in-memory telemetry logger."""
        self.session_id = str(uuid.uuid4())
        self.memory_store = []

    def emit(
        self,
        iteration: int,
        cumulative_latency_ms: float,
        scores: dict,
        response_feedback: dict,
        residual_error: float,
        failed_instructions_count: int,
        stop_reason: str,
        response_text: str,
        prompt: str = "",
    ):
        """
        Emit a single telemetry entry.

        Args:
            iteration (int): The iteration number of the pipeline (starts at 1).
            cumulative_latency_ms (float): Total latency from pipeline start (ms).
            scores (dict): Evaluation scores (e.g., groundedness, instruction adherence).
            response_feedback (dict): Feedback for failed instructions.
            residual_error (int): Residual error score.
            failed_instructions_count (int): Count of instructions not followed.
            stop_reason (str): Reason for stopping or continuing.
            response_text (str): The raw text response from the LLM.
            prompt (str): The prompt text used for this iteration.
        """
        telemetry = {
            # not returned
            "_timestamp": datetime.utcnow().isoformat() + "Z",
            "_session_id": self.session_id,
            # returned
            "iteration": iteration,
            "cumulative_latency_ms": cumulative_latency_ms,
            "scores": scores,
            "response_feedback": response_feedback,
            "residual_error": residual_error,
            "failed_instructions_count": failed_instructions_count,
            "stop_reason": stop_reason,
            "prompt_template": prompt,
            "response_text": response_text,
        }
        self.memory_store.append(telemetry)

    def get_all(self, include_meta=False):
        """
        Return all recorded telemetry entries.

        Args:
            include_meta (bool): If True, includes session_id and timestamp. Defaults to False.

        Returns:
            list: Telemetry entries, stripped of internal metadata unless requested.
        """
        if include_meta:
            return self.memory_store
        # Strip out keys starting with "_" for external return
        sanitized = []
        for entry in self.memory_store:
            sanitized.append({k: v for k, v in entry.items() if not k.startswith("_")})
        return sanitized
