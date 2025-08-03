"""
runner.py — This module provides a high-level function (`run_reprompting_pipeline`) 
for executing AIMon's iterative re-prompting workflow.

This function is the primary entry point for developers and end-users. It:
    - Normalizes inputs (replacing missing `system_prompt` or `context` with clear placeholders).
    - Initializes the `RepromptingPipeline` with the provided configuration and LLM function.
    - Runs the full re-prompting loop, generating an initial response, evaluating it,
      and iteratively re-prompting until adherence criteria or stopping conditions are met.

Contributors can extend this behavior by modifying `RepromptingPipeline` or `RepromptingConfig`.
"""
from typing import List, Optional
from aimon.reprompting_api.pipeline import RepromptingPipeline
from aimon.reprompting_api.config import RepromptingConfig

def run_reprompting_pipeline(
    llm_fn,
    user_query: str,
    system_prompt: str = None,
    context:str = None,
    user_instructions: List[str] = None,
    reprompting_config: RepromptingConfig = None,
) -> dict:
    """
    High-level wrapper for running the full AIMon re-prompting pipeline.

    This function prepares and normalizes all inputs, initializes the pipeline,
    and executes the iterative re-prompting process. Missing `system_prompt` or 
    `context` values are replaced with clear placeholders (`"[no system prompt provided]"` 
    and `"[no context provided]"`) to ensure template consistency.

    Args:
        llm_fn (Callable[[Template, str, str, str], str]): A function to call the LLM. Must accept a prompt template (recommended_prompt_template), 
        `system_prompt`, `context`, and `user_query`.
        user_query (str): The user’s query. Must be a non-empty string.
        system_prompt (str, optional): A system-level instruction string. Defaults to `"[no system prompt provided]"` if None or empty.
        context (str, optional): Supplemental context for the LLM. Defaults to `"[no context provided]"` if None or empty.
        user_instructions (List[str], optional): A list of instructions for the model to follow. Defaults to an empty list.
        reprompting_config (RepromptingConfig, optional): Configuration object for controlling pipeline behavior.

    Returns:
        dict: A structured dictionary containing:
            - "best_response" (str): The final, best LLM response.
            - "telemetry" (list, optional): Iteration-level telemetry if enabled in config.
            - "summary" (str, optional): A human-readable summary of the process if enabled.
    """

    # Use the provided config or fall back to defaults
    config = reprompting_config or RepromptingConfig()
    
    # validate llm_fn
    if not callable(llm_fn):
        raise TypeError("llm_fn must be a callable that returns a string.")

    if not user_query or not isinstance(user_query, str):
        raise ValueError("user_query must be a non-empty string.")
    
    context = context if (context and isinstance(context, str)) else "[no context provided]"
    system_prompt = system_prompt if (system_prompt and isinstance(system_prompt, str)) else "[no system prompt provided]"

    # initialize the re-prompting pipeline with the LLM function and configuration
    pipeline = RepromptingPipeline(llm_fn=llm_fn, config=config)
    
    return pipeline.run(
        system_prompt=system_prompt,
        context=context,
        user_query=user_query,
        user_instructions=user_instructions or [] # Default to empty list if none provided
    )