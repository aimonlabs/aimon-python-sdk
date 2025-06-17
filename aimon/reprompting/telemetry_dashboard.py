import streamlit as st
import json
import pandas as pd

st.set_page_config(layout="wide")
st.title("LLM Reprompt Telemetry Dashboard")

with open("telemetry_log.jsonl") as f:
    logs = [json.loads(line) for line in f]

# Filter by event or session if needed
iterations = [log["iteration"] for log in logs]
halluc_scores = [log["scores"].get("hallucination") for log in logs]
instr_scores = [log["scores"].get("instruction_adherence") for log in logs]
latency = [log["latency_ms"] for log in logs]

# Charts
st.subheader("Score Trends")
st.line_chart({
    "Hallucination Score": halluc_scores,
    "Instruction Adherence": instr_scores
})

st.subheader("Latency (ms)")
st.line_chart({"Latency": latency})

st.subheader("Detailed Logs")
for log in logs:
    with st.expander(f"Iteration {log['iteration']} | Stop: {log['stop_reason']}"):
        st.write(log["scores"])
        st.write(log["error_vector"])
        st.code(log["response_text"])

# Build a table DataFrame
table_data = []

for log in logs:
    table_data.append({
        "Iteration": log["iteration"],
        "Prompt Tokens": log["token_counts"].get("prompt_tokens"),
        "Response Tokens": log["token_counts"].get("response_tokens"),
        "Instruction Adherence": log["scores"].get("instruction_adherence"),
        "Hallucination": log["scores"].get("hallucination"),
        "Latency (ms)": round(log["latency_ms"], 2),
        "Stop Reason": log.get("stop_reason", "N/A")
    })

df_table = pd.DataFrame(table_data)

# Sort by iteration
df_table = df_table.sort_values("Iteration").reset_index(drop=True)

# Display as table
st.subheader("📊 Per-Iteration Summary Table")
st.dataframe(df_table.style.format({
    "Instruction Adherence": "{:.3f}",
    "Hallucination": "{:.3f}",
    "Latency (ms)": "{:.2f}"
}))

