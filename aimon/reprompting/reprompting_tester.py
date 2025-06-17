import csv
import json
from coordinator import ReactConfig, Coordinator
from reprompter import Reprompter
from agent import Agent
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize configuration and components
config = ReactConfig(
    publish=True,
    max_attempts=5,
    aimon_api_key="998e211045c1d9e5b1fc0fa9e9e001be684596d8d529952c088eb1627480529c"
)
reprom = Reprompter()
agent = Agent()

# Input and output files
input_csv = "test_cases.csv"
output_csv = "telemetry_results.csv"

# Load all test cases
with open(input_csv, newline='', encoding='utf-8') as infile:
    reader = list(csv.DictReader(infile))

# Define single test case runner
def run_test_case(row):
    test_case_id = row["test_case_id"]
    model = int(row["model_num"])
    model_name = row["model_name"]
    context = row["context_docs"]
    query = row["user_query"]
    instructions = json.loads(row["instructions"]) if isinstance(row["instructions"], str) else row["instructions"]

    local_coordinator = Coordinator(
        llm_app=None,
        react_configuration=config,
        context_extractor=None,
        reprompter=reprom,
        agent=agent
    )

    try:
        telemetry = local_coordinator.coordinate(model, context, query, instructions)
        rows = []
        for entry in telemetry:
            rows.append({
                "test_case_id": test_case_id,
                "model_name": model_name,
                "iteration": entry["iteration"],
                "latency_ms": entry["latency_ms"],
                "prompt_tokens": entry["prompt_tokens"],
                "response_tokens": entry["response_tokens"],
                "hallucination_score": entry["scores"]["hallucination"],
                "instruction_adherence_score": entry["scores"]["instruction_adherence"],
                "residual_error": entry["residual_error"],
                "stop_reason": entry["stop_reason"],
                "prompt": entry["prompt"],
                "response_text": entry["response_text"],
                "error_vector": json.dumps(entry["error_vector"])
            })
        return rows
    except Exception as e:
        print(f"[ERROR] Test case {test_case_id} ({model_name}): {e}")
        return []

# Run test cases in parallel
results = []
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(run_test_case, row) for row in reader]
    for future in as_completed(futures):
        results.extend(future.result())

# Write results to output CSV
fieldnames = [
    "test_case_id", "model_name", "iteration", "latency_ms", "prompt_tokens", "response_tokens",
    "hallucination_score", "instruction_adherence_score", "residual_error",
    "stop_reason", "prompt", "response_text", "error_vector"
]

with open(output_csv, "w", newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)