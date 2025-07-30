import os
import logging
from string import Template
from together import Together
from aimon.reprompting_api.config import RepromptingConfig
from aimon.reprompting_api.runner import run_reprompting_pipeline

# --- Configure logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Load API keys ---
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
AIMON_API_KEY = os.environ.get("AIMON_API_KEY")
if not TOGETHER_API_KEY or not AIMON_API_KEY:
    logger.warning("API keys are missing. Make sure TOGETHER_API_KEY and AIMON_API_KEY are set.")

# --- Initialize Together client ---
client = Together(api_key=TOGETHER_API_KEY)

# --- LLM Function ---
def my_llm(recommended_prompt_template: Template, system_prompt=None, context=None, user_query=None) -> str:
    """
    Example LLM function that:
      1. Receives a corrective prompt template (string.Template).
      2. Substitutes placeholders (system_prompt, context, user_query).
      3. Sends to a Together-hosted LLM and returns the response.
    """
    filled_prompt = recommended_prompt_template.substitute(
        system_prompt=system_prompt or "",
        context=context or "",
        user_query=user_query or ""
    )
    logger.info(f"[LLM] Sending prompt to model: {filled_prompt[:200]}...")  # Log preview

    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": filled_prompt}],
        max_tokens=256,
        temperature=0
    )
    output = response.choices[0].message.content
    logger.info(f"[LLM] Received response: {output[:200]}...")
    return output

# --- Test Case: Successful Run ---
def test_successful_run():
    """
    Simulates a realistic pipeline run with:
    - Complex context
    - Query for simplification
    - Multiple style/tone instructions
    - Telemetry & summary enabled
    """
    logger.info("[Pipeline] Starting test run...")
    
    config = RepromptingConfig(
        aimon_api_key=AIMON_API_KEY,
        publish=True,
        return_telemetry=True,
        return_aimon_summary=True,
        application_name="api_test",
        max_iterations=3
    )
    logger.info("[Pipeline] Config prepared.")

    user_query = "what are the drug tiers?"
    context = "[SECTION] 📘 BlueShield Rx Policy Addendum: 2023–2025 ... (truncated for brevity)"
    user_instructions = [
        "Avoid overly technical or robotic phrasing; keep the tone human and accessible.",
        "Ensure the response is direct and professional, with minimal informal tone.",
        "Translate or simplify technical details from the context into accurate, user-friendly explanations.",
        "Don't use the letter e",
        "only use the letter e"
    ]
    logger.info(f"[Pipeline] User query: {user_query}")
    logger.info(f"[Pipeline] Context: {context[:100]}...")
    logger.info(f"[Pipeline] Instructions: {user_instructions}")

    # Run pipeline
    result = run_reprompting_pipeline(
        llm_fn=my_llm,
        user_query=user_query,
        system_prompt="here is a system prompt",
        context=context,
        user_instructions=user_instructions,
        reprompting_config=config
    )

    # Log each part of the result
    logger.info("[Pipeline] Run complete.")
    logger.info(f"[Pipeline] Best Response: {result['best_response']}")
    logger.info(f"[Pipeline] Telemetry: {result.get('telemetry')}")
    logger.info(f"[Pipeline] Summary: {result.get('summary')}")

    # Print outputs for inspection
    print("\n=== BEST RESPONSE ===")
    print(result["best_response"])
    print("\n=== TELEMETRY ===")
    print(result.get("telemetry"))
    print("\n=== SUMMARY ===")
    print(result.get("summary"))

# --- Entry Point ---
if __name__ == "__main__":
    test_successful_run()
