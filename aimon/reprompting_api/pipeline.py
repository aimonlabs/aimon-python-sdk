from aimon.reprompting_api.config import RepromptingConfig, StopReasons
from aimon.reprompting_api.telemetry import TelemetryLogger
from aimon.reprompting_api.reprompter import Reprompter
from aimon.reprompting_api.utils import retry, toxicity_check, get_failed_instructions_count, get_failed_instructions, get_residual_error_score, get_failed_toxicity_instructions
from aimon import Detect
import time
import random
from string import Template
import logging

logger = logging.getLogger(__name__)

class RepromptingPipeline:
    """
    A pipeline for iterative re-prompting of LLM responses using AIMon evaluation.
    
    This pipeline orchestrates:
      - Initial prompt generation for a given query, context, and user instructions.
      - Interaction with a black-box LLM to generate responses.
      - Evaluation of responses using AIMon detectors (instruction adherence, groundedness, toxicity).
      - Iterative corrective re-prompting until stopping conditions are met.
      - Collection and emission of telemetry for all iterations.
      
    **Expected LLM function signature**:
        llm_fn(recommended_prompt_template: Template, system_prompt: str, context: str, user_query: str) -> str
      
    Attributes:
        llm_fn (callable): Function to call the LLM. Must be a Callable with
            -recommended_prompt_template: Template
            -system_prompt: str
            -context: str
            -user_query: str

        config (RepromptingConfig): Configuration object with API keys and iteration limits.
        reprompter (Reprompter): Utility for generating corrective prompts based on evaluation feedback.
        telemetry (TelemetryLogger): Logger for capturing telemetry data.
        detect (Detect): AIMon detection client for evaluating model responses.
        
    Returns:
        dict:
            {
                "best_response" (str): Best model response across all iterations.
                "telemetry" (list, optional): Iteration-level telemetry if enabled.
                "summary" (str, optional): Human-readable run summary if enabled.
            }
    """
    def __init__(self, llm_fn, config):
        """
        Initialize pipeline with LLM callable and RepromptingConfig.
        
        Args:
            llm_fn (callable): Function to call the LLM. 
                Signature: llm_fn(recommended_prompt_template: Template, system_prompt: str, context: str, user_query: str) -> str
            config (RepromptingConfig): Configuration object with API keys and limits.

        """
        self.llm_fn = llm_fn
        self.config = config or RepromptingConfig()
        
        # Utilities for reprompting, telemetry, and scoring
        self.reprompter = Reprompter()
        self.telemetry = TelemetryLogger()

        # Initialize AIMon Detect for response evaluation
        self.detect = Detect(
            values_returned=['user_query', 'instructions', 'generated_text', 'context'],
            config={
                "instruction_adherence": {
                    "detector_name": "default",
                    "explain": True,
                    "extract_from_system": False
                },
                "groundedness": {
                    "detector_name": "default",
                    "explain": True
                },
                "toxicity": {
                    "detector_name": "default",
                    "explain": True
                }
            },
            api_key=self.config.aimon_api_key,
            application_name = self.config.application_name,
            model_name = self.config.model_name,
            publish=self.config.publish
        )
        
    def run(self, system_prompt: str, context: str, user_query: str, user_instructions):
        """
        Execute the full re-prompting pipeline.
        
        Process:
          1. Build an initial prompt with query, context, and instructions.
          2. Call the LLM to generate a response.
          3. Evaluate the response with AIMon detectors for instruction adherence, toxicity, and groundedness.
          Toxicity and groundedness are always evaluated. If user_instructions are empty / not provided, the 
          instruction adherence detector is not used.
          4. If violations are found, iteratively generate corrective prompts and re-prompt the LLM.
          5. Stop when all instructions are followed and response has no hallucination or toxicity or when iteration or latency limits are reached.
          6. Return the best response (lowest residual error) along with telemetry and a summary if configured.
        
        Args:
            user_query (str): Must be a non-empty string. The user's query or instruction.
            context (str): Contextual information to include in the prompt. May be an empty string, but it is recommended to be included. 
            user_instructions (list[str]): Instructions the model must follow. May be an empty list, but it is highly recommended to be included.
            system_prompt (str): A high‑level role or behavior definition for the model. May be an empty string.

        Returns:
            dict: 
                {
                    "best_response" (str): Best model response from all iterations.
                    "telemetry" (list, optional): Telemetry for all iterations if enabled.
                    "summary" (str, optional): Summary of the process if enabled.
                }
        """
        logger.info("Starting RepromptingPipeline run")
        logger.debug(f"Inputs - System Prompt: {system_prompt}, Context: {context}, User Query: {user_query}, Instructions: {user_instructions}")
        iteration_outputs = {} # key: iteration number → dict(response_text, residual_error_score, failed_instructions_count)
        pipeline_start = time.time()
        iteration_num = 1

        curr_prompt = self._build_original_prompt()
        logger.debug(f"Initial prompt template built: {curr_prompt.template}")

        
        # First LLM call
        curr_generated_text = self._call_llm(curr_prompt,self.config.user_model_max_retries, system_prompt, context, user_query)
        logger.debug(f"Initial LLM response: {curr_generated_text}")

        
        # Evaluate response with AIMon
        curr_payload = self._build_aimon_payload(context, user_query, user_instructions, curr_generated_text, system_prompt)
        curr_result = self._detect_aimon_response(curr_payload, self.config.feedback_model_max_retries)
        logger.debug(f"AIMon evaluation result: {curr_result}")
        
        # Get scores and detailed feedback on failed instructions
        scores, feedback = self.get_response_feedback(curr_result)
        self._record_iteration_output(iteration_outputs, iteration_num, curr_generated_text, curr_result)

        # Iteratively re-prompt until conditions are met or limits reached
        stop_reason = None
        while True:
            should_stop, stop_reason = self._should_stop_reprompting(curr_result, iteration_num, pipeline_start)
            logger.info(f"Iteration {iteration_num}: Stop decision: {should_stop}, Reason: {stop_reason}")
            if should_stop:
                break
            
            # Emit telemetry for this iteration
            self._emit_iteration_telemetry(
                iteration_num,
                pipeline_start,
                scores,
                feedback,
                curr_result,
                stop_reason or StopReasons.CONTINUE,
                curr_prompt,
                curr_generated_text,
            )

            # Generate corrective prompt
            curr_prompt = self._build_corrective_prompt(curr_payload, curr_result)
            
            # Retry LLM call with corrective prompt
            curr_generated_text = self._call_llm(curr_prompt, self.config.user_model_max_retries)
            curr_generated_text = self._call_llm(curr_prompt,self.config.user_model_max_retries, system_prompt, context, user_query)
            # Re-evaluate the new response
            curr_payload = self._build_aimon_payload(context, user_query, user_instructions, curr_generated_text, system_prompt)
            curr_result = self._detect_aimon_response(curr_payload, self.config.feedback_model_max_retries)

            # Extract updated scores and feedback
            scores, feedback = self.get_response_feedback(curr_result)
            iteration_num += 1
            self._record_iteration_output(iteration_outputs, iteration_num, curr_generated_text, curr_result)

        # Final telemetry after loop exit
        self._emit_iteration_telemetry(
            iteration_num,
            pipeline_start,
            scores,
            feedback,
            curr_result,
            stop_reason or StopReasons.UNKNOWN_ERROR,
            curr_prompt,
            curr_generated_text,
        )

        # Select best response across all iterations
        best_output, best_failed_count = self._select_best_iteration(iteration_outputs)
            
        # Build final response payload
        response = {"best_response": best_output}
        if self.config.return_telemetry:
            response["telemetry"] = self.telemetry.get_all()
        if self.config.return_aimon_summary:
            response["summary"] = self._gen_summary(iteration_num, best_failed_count)
            
        logger.info("RepromptingPipeline run completed")
        logger.info(f"Best response selected with {best_failed_count} failed instructions remaining.")

        return response  

    def _build_original_prompt(self) -> Template:
        """
        Build a reusable template for combining system_prompt, context, and user_query.
        This returns a string.Template object so the caller can safely substitute values.
        
        Placeholders:
            - system_prompt
            - context
            - user_query

        Returns:
            Template: A string.Template for building the base LLM prompt.
        """
        template_str = (
            "System:\n${system_prompt}\n\n"
            "Context:\n${context}\n\n"
            "User Query:\n${user_query}"
        )
        return Template(template_str)

    def _build_aimon_payload(self, context, user_query, user_instructions, generated_text, system_prompt):
        """
        Constructs AIMon input payload.

        Args:
            context (str): Context for the LLM.
            user_query (str): The user's query.
            user_instructions (list[str]): Instructions for the model.
            generated_text (str): The model's generated response.

        Returns:
            dict: Payload for AIMon evaluation.
        """
        if not isinstance(user_instructions, list):
            user_instructions = []
        payload = {
            'context': context,
            'user_query': user_query,
            'generated_text': generated_text,
            'instructions': user_instructions,
            'system_prompt' : system_prompt
        }
        return payload

    def _call_llm(self, prompt_template: Template, max_attempts, system_prompt=None, context=None, user_query=None):
        """
        Calls the LLM with exponential backoff. Retries if the LLM call fails
        OR returns a non-string value.  If all retries fail, the last encountered
        exception from the LLM call is re-raised.

        Args:
            prompt_template (Template): Prompt template for the LLM.
            max_attempts (int): Max retry attempts.
            
        Returns:
            str: LLM response text.

        Raises:
            RuntimeError: If the LLM call repeatedly fails, re-raises the last encountered error.
            TypeError: If the LLM call fails to return a string.
        """
        @retry(exception_to_check=Exception, tries=max_attempts, delay=1, backoff=2, logger=logger)
        def backoff_call():
            result = self.llm_fn(prompt_template, system_prompt, context, user_query)
            if not isinstance(result, str):
                raise TypeError(f"LLM returned invalid type {type(result).__name__}, expected str.")
            return result
        return backoff_call()
    
    def _detect_aimon_response(self, payload, max_attempts):
        """
        Calls AIMon Detect with exponential backoff and returns the detection result.

        This method wraps the AIMon evaluation call, retrying if it fails due to transient 
        errors (e.g., network issues or temporary service unavailability). It retries up to 
        `max_attempts` times with exponential backoff before raising the last encountered 
        exception from the AIMon Detect call.

        Args:
            payload (dict): A dictionary containing 'context', 'user_query', 
                            'instructions', and 'generated_text' for evaluation.
            max_attempts (int): Maximum number of retry attempts.

        Returns:
            object: The AIMon detection result containing evaluation scores and feedback.

        Raises:
            RuntimeError: If AIMon Detect fails after all retry attempts, re-raises the last encountered error.
        """
        aimon_context = f"{payload['context']}\n\nUser Query:\n{payload['user_query']}"
        aimon_query = f"{payload['user_query']}\n\nInstructions:\n{payload['instructions']}"
        
        @self.detect
        def run_detection(query, instructions, generated_text, context):
            return query, instructions, generated_text, context

        @retry(
            exception_to_check=Exception,
            tries=max_attempts,
            delay=1,
            backoff=2,
            logger=logger
        )
        def inner_detection():
            logger.debug(f"AIMon detect call with payload: {payload}")
            _, _, _, _, result = run_detection(
                aimon_query,
                payload['instructions'],
                payload['generated_text'],
                aimon_context
            )
            return result
        return inner_detection()

    def get_response_feedback(self, result):
            """
            Extract groundedness and instruction adherence scores and failed instructions.
            
            Args:
                result (object): AIMon detection result.

            Returns:
                tuple: (scores (dict), failed_instructions (list))
            """
            scores = {
                "groundedness": result.detect_response.groundedness.get("score", 0.0),
                "instruction_adherence": result.detect_response.instruction_adherence.get("score", 0.0),
                "toxicity": result.detect_response.toxicity.get("score", 0.0)
            }
            feedback = get_failed_instructions(result) + get_failed_toxicity_instructions(result)
            return scores, feedback
    
    def _build_corrective_prompt(self, payload, result):
        """
        Generate a corrective prompt using AIMon evaluation results.

         Args:
            payload (dict): AIMon input payload.
            result (object): AIMon detection result.

        Returns:
            str: A corrective prompt for re-prompting the LLM.
        """
        return self.reprompter.create_corrective_prompt(result, payload)

    def _should_stop_reprompting(self, result, iteration_num, pipeline_start):
        """
        Determine whether to stop re-prompting. 
        
        Stopping conditions:
        - Max iterations reached.
        - Latency budget 75% depleted
        - All instructions are adhered to.
        - Otherwise, continue if violations or toxicity remain.
        
        Args:
            result (object): AIMon detection result.
            iteration_num (int): Current iteration number.
            
        Returns:
            tuple: 
                (should_stop (bool), stop_reason (str or None))
        """
        # Max iterations reached
        if iteration_num >= self.config.max_iterations:
            return True, StopReasons.MAX_ITERATIONS_REACHED
        
        latency_limit_ms = self.config.latency_limit_ms
        if latency_limit_ms is not None:
            cumulative_latency = self._get_cumulative_latency(pipeline_start)
            if cumulative_latency > ((0.75) * latency_limit_ms):
                return True, StopReasons.LATENCY_LIMIT_EXCEEDED
        
        # Continue if toxicity is detected
        if toxicity_check(result):
            return False, StopReasons.CONTINUE_TOXICITY

        # Continue if there are still failed instructions
        if get_failed_instructions_count(result) > 0:
            return False, StopReasons.CONTINUE

        # All instructions followed
        return True, StopReasons.ALL_INSTRUCTIONS_ADHERED

    def _select_best_iteration(self, iteration_outputs):
        """
        Selects the best iteration based on the lowest residual error score.

        Args:
            iteration_outputs (dict): Mapping of iteration_num -> iteration data.

        Returns:
            tuple: (best_output (str), best_failed_count (int))
        """
        valid_iterations = [
            entry for entry in iteration_outputs.values()
            if isinstance(entry.get("residual_error_score"), (int, float))
        ]
        if not valid_iterations:
            return "[ERROR: No valid response]", None

        best_iteration = min(valid_iterations, key=lambda x: x["residual_error_score"])
        return best_iteration["response_text"], best_iteration["failed_instructions_count"]
    
    def _gen_summary(self, iteration_num, best_failed_count):
        """
        Generate a human-readable summary for the pipeline run.
            e.g.: "2 iterations, 0 failed instructions remaining"

        Args:
            iteration_num (int): Number of iterations performed.
            best_failed_count (int): Number of failed instructions in the best response.

        Returns:
            str: Summary.
        """
        iteration_word = "iteration" if iteration_num == 1 else "iterations"
        summary = f"{iteration_num} {iteration_word}, {best_failed_count} failed instructions remaining"
        return summary
    
    def _build_telemetry_entry(
        self,
        iteration,
        cumulative_latency,
        scores,
        feedback,
        residual_error,
        failed_count,
        stop_reason,
        prompt,
        response_text,
    ):
        """
        Build a structured telemetry entry for an iteration.

        Args:
            iteration (int): Iteration number.
            cumulative_latency (float): Total latency in milliseconds so far.
            scores (dict): Evaluation scores.
            feedback (list): Failed instruction feedback.
            residual_error (float): Residual error score.
            failed_count (int): Number of failed instructions.
            stop_reason (str): Reason for stopping.
            prompt (str): Prompt used for this iteration.
            response_text (str): Model's response.

        Returns:
            dict: Structured telemetry entry.
        """
        return {
            "iteration": iteration,
            "cumulative_latency_ms": cumulative_latency,
            "scores": scores,
            "response_feedback": feedback,
            "residual_error": residual_error,
            "failed_instructions_count": failed_count,
            "stop_reason": stop_reason,
            "prompt": prompt,
            "response_text": response_text,
        }

    def _emit_iteration_telemetry(
        self,
        iteration_num,
        pipeline_start,
        scores,
        feedback,
        curr_result,
        stop_reason,
        curr_prompt,
        curr_generated_text,
    ):
        """
        Build and emit telemetry for an iteration. Calculates cumulative latency.

        Args:
            iteration_num (int): Current iteration number.
            pipeline_start (float): Start time of the pipeline (epoch).
            scores (dict): Evaluation scores.
            feedback (list): Failed instruction feedback.
            curr_result (object): AIMon detection result.
            stop_reason (str): Reason for stopping or continuing.
            curr_prompt (str): Prompt used.
            curr_generated_text (str): Model response text.

        Returns:
            dict: The telemetry entry.
        """
        cumulative_latency_ms = self._get_cumulative_latency(pipeline_start)
        
        residual_error = get_residual_error_score(curr_result) if curr_result else None
        failed_count = get_failed_instructions_count(curr_result) if curr_result else None
        
        prompt_text = curr_prompt.template 
        
        entry = self._build_telemetry_entry(
            iteration_num,
            cumulative_latency_ms,
            scores,
            feedback,
            residual_error,
            failed_count,
            stop_reason,
            prompt_text,
            curr_generated_text,
        )
        try:
            self.telemetry.emit(**entry)
        except Exception as e:
            logger.warning(f"[Warning] Telemetry emission failed: {e}")
        return entry
    
    def _get_cumulative_latency(self, pipeline_start):
        """
        Calculate cumulative latency since pipeline start.

        Args:
            pipeline_start (float): Start time of the pipeline (epoch).

        Returns:
            float: Cumulative latency in milliseconds.
        """
        return (time.time() - pipeline_start) * 1000
    
    def _record_iteration_output(self, iteration_outputs, iteration_num, generated_text, result):
        """
        Record iteration outputs for later selection of the best response.

        Args:
            iteration_outputs (dict): Stores outputs per iteration.
            iteration_num (int): Current iteration number.
            generated_text (str): Model's generated response.
            result (object): AIMon detection result.

        Returns:
            None
        """
        iteration_outputs[iteration_num] = {
            "response_text": generated_text,
            "residual_error_score": get_residual_error_score(result),
            "failed_instructions_count": get_failed_instructions_count(result)
        }