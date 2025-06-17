import json
import time
import uuid
from datetime import datetime
from pathlib import Path

class TelemetryLogger:
    def __init__(self, log_path="telemetry_log.jsonl"):
        self.session_id = str(uuid.uuid4())
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        iteration: int,
        latency_ms: float,
        prompt_tokens: int,
        response_tokens: int,
        scores: dict,
        error_vector: dict,
        residual_error: int,
        stop_reason: str,
        response_text: str,
        prompt: str = "",
    ):
        telemetry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id,
            "iteration": iteration,
            "latency_ms": latency_ms,
            "token_counts": {
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens
            },
            "scores": scores,
            "error_vector": error_vector,
            "residual_error": residual_error,
            "stop_reason": stop_reason,
            "prompt": prompt,
            "response_text": response_text
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(telemetry) + "\n")
