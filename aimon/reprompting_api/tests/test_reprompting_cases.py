import os
import pytest
from string import Template
from together import Together
from aimon.reprompting_api.config import RepromptingConfig
from aimon.reprompting_api.runner import run_reprompting_pipeline

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
AIMON_API_KEY = os.environ.get("AIMON_API_KEY")

client = Together(api_key=TOGETHER_API_KEY)

# --- Fixtures ---

@pytest.fixture
def my_llm():
    def _my_llm(recommended_prompt_template: Template, system_prompt, context, user_query) -> str:
        filled_prompt = recommended_prompt_template.substitute(
            system_prompt=system_prompt or "",
            context=context or "",
            user_query=user_query or ""
        )
        print("====prompt===")
        print(filled_prompt)
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[{"role": "user", "content": filled_prompt}],
            max_tokens=256,
            temperature=0
        )
        return response.choices[0].message.content
    return _my_llm

@pytest.fixture
def base_config():
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=2,
    )

@pytest.fixture
def config_without_telemetry():
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=False,
        return_aimon_summary=False,
        application_name="api_test",
        max_iterations=2,
    )

@pytest.fixture
def config_low_latency():
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=2,
        latency_limit_ms=100
    )

@pytest.fixture
def config_high_latency():
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=3,
        latency_limit_ms=5000
    )

@pytest.fixture
def config_iteration_limit():
    return RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=False,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=-1,
    )

# --- Tests ---

@pytest.mark.integration
def test_low_latency_limit(my_llm, config_low_latency):
    result = run_reprompting_pipeline(
        user_query="Test latency limit termination return",
        context="Context",
        llm_fn=my_llm,
        reprompting_config=config_low_latency,
        user_instructions=[]
    )
    assert "best_response" in result

@pytest.mark.integration
def test_latency_limit(my_llm, config_high_latency):
    result = run_reprompting_pipeline(
        user_query="What is context?",
        context="Context",
        llm_fn=my_llm,
        reprompting_config=config_high_latency,
        user_instructions=["Do not use the letter e", "Only use the letter e"]
    )
    assert "best_response" in result

@pytest.mark.integration
def test_iteration_limit(my_llm, config_iteration_limit):
    result = run_reprompting_pipeline(
        user_query="What's the policy?",
        context="hi",
        llm_fn=my_llm,
        reprompting_config=config_iteration_limit,
        user_instructions=[]
    )
    assert "best_response" in result

@pytest.mark.integration
def test_empty_context_and_instructions(my_llm, base_config):
    result = run_reprompting_pipeline(
        user_query="What's the policy?",
        context="",
        llm_fn=my_llm,
        reprompting_config=base_config,
        user_instructions=[]
    )
    assert "best_response" in result

@pytest.mark.integration
def test_no_telemetry(my_llm, config_without_telemetry):
    result = run_reprompting_pipeline(
        user_query="What's the policy?",
        context="Context for telemetry disabled run",
        llm_fn=my_llm,
        reprompting_config=config_without_telemetry,
        user_instructions=[]
    )
    assert "telemetry" not in result
    assert "summary" not in result

@pytest.mark.integration
def test_no_system_prompt(my_llm, base_config):
    result = run_reprompting_pipeline(
        user_query="What's the policy?",
        context="Context for telemetry disabled run",
        llm_fn=my_llm,
        reprompting_config=base_config,
        user_instructions=["use the letter e only", "do not use the letter e"]
    )
    assert "best_response" in result

@pytest.mark.integration
def test_with_system_prompt(my_llm, base_config):
    result = run_reprompting_pipeline(
        user_query="What's the policy?",
        context="Context for telemetry disabled run",
        llm_fn=my_llm,
        reprompting_config=base_config,
        user_instructions=["use the letter e only", "do not use the letter e", "use a neutral tone"],
        system_prompt="this is a system prompt"
    )
    assert "best_response" in result
    assert "telemetry" in result
    assert "summary" in result
