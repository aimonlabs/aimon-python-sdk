import os
import pytest
from string import Template
import aimon
from aimon.reprompting_api.config import RepromptingConfig
from aimon.reprompting_api.runner import run_reprompting_pipeline

AIMON_API_KEY = os.environ.get("AIMON_API_KEY")

# --- MOCKED LLM FUNCTIONS ---
def my_llm(prompt_template: Template, system_prompt=None, context=None, user_query=None) -> str:
    """Simulates a normal working LLM that returns a string response. Just returns filled_prompt for test"""
    filled_prompt = prompt_template.safe_substitute(
        system_prompt=system_prompt or "",
        context=context or "",
        user_query=user_query or ""
    )
    return filled_prompt

def llm_fn_failure(prompt_template: Template, system_prompt=None, context=None, user_query=None) -> str:
    """Simulates an LLM call that fails every time."""
    raise RuntimeError("LLM call failed intentionally for testing")

def llm_fn_incorrect_return_value(prompt_template: Template, system_prompt=None, context=None, user_query=None):
    """Simulates an LLM that returns an invalid type instead of a string."""
    return 42

# --- MOCKED CONFIG FACTORIES ---
def get_config():
    """Returns a valid base configuration for most tests."""
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=2,
    )

def get_config_with_invalid_aimon_api_key():
    """Returns a config with an intentionally invalid AIMon API key."""
    return RepromptingConfig(
        aimon_api_key="invalid key",
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=3,
    )

# --- TESTS EXPECTING FAILURES ---
def test_llm_failure():
    """Should raise RuntimeError when the LLM function always fails."""
    config = get_config()
    with pytest.raises(RuntimeError, match="LLM call failed intentionally for testing"):
        run_reprompting_pipeline(
            user_query="Test LLM failure handling",
            context="Context for failure test",
            llm_fn=llm_fn_failure,
            reprompting_config=config,
            user_instructions=[]
        )

def test_invalid_llm_fn():
    """Should raise TypeError when LLM function is None."""
    config = get_config()
    with pytest.raises(TypeError):
        run_reprompting_pipeline(
            user_query="Test invalid LLM fn",
            context="Context for failure test",
            llm_fn=None,
            reprompting_config=config,
            user_instructions=[]
        )

def test_invalid_return_value():
    """Should raise TypeError when the LLM returns a non-string value."""
    config = get_config()
    with pytest.raises(TypeError, match="LLM returned invalid type int, expected str."):
        run_reprompting_pipeline(
            user_query="Test invalid return type",
            context="Context for type error",
            llm_fn=llm_fn_incorrect_return_value,
            reprompting_config=config,
            user_instructions=[]
        )

def test_empty_query():
    """Empty query should raise a ValueError."""
    config = get_config()
    with pytest.raises(ValueError, match="user_query must be a non-empty string"):
        run_reprompting_pipeline(
            user_query="",
            context="",
            llm_fn=my_llm,
            reprompting_config=config,
            user_instructions=[]
        )

def test_invalid_api_key():
    """Should fail due to invalid AIMon API key."""
    config = get_config_with_invalid_aimon_api_key()
    with pytest.raises(aimon.AuthenticationError):
        run_reprompting_pipeline(
            user_query="Testing with invalid AIMon API key",
            context="Context for invalid key test",
            llm_fn=my_llm,
            reprompting_config=config,
            user_instructions=[]
        )
