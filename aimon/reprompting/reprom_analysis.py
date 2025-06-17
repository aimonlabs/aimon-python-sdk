import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

input_csv = "telemetry_results.csv"

# Containers
scores_per_iteration = defaultdict(lambda: {
    "residual": [],
    "ia": [],
    "halluc": [],
    "latency": [],
    "failed_instructions": []
})
last_scores = {}  # test_case_id -> (res, ia, halluc, latency, failed_count, iter)

# Read data
with open(input_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        test_case_id = row["test_case_id"]
        iter_num = int(row["iteration"])
        residual = float(row["residual_error"])
        ia = float(row["instruction_adherence_score"])
        halluc = float(row["hallucination_score"])
        latency = float(row["latency_ms"])
        errors = json.loads(row["error_vector"])
        failed_count = len(errors)

        scores_per_iteration[iter_num]["residual"].append(residual)
        scores_per_iteration[iter_num]["ia"].append(ia)
        scores_per_iteration[iter_num]["halluc"].append(halluc)
        scores_per_iteration[iter_num]["latency"].append(latency)
        scores_per_iteration[iter_num]["failed_instructions"].append(failed_count)

        last_scores[test_case_id] = (residual, ia, halluc, latency, failed_count, iter_num)

# Pad later iterations for test cases that converged early
max_iter = max(scores_per_iteration.keys())
for test_case_id, (res, ia, hall, lat, fail_cnt, last_iter) in last_scores.items():
    for pad_iter in range(last_iter + 1, max_iter + 1):
        scores_per_iteration[pad_iter]["residual"].append(res)
        scores_per_iteration[pad_iter]["ia"].append(ia)
        scores_per_iteration[pad_iter]["halluc"].append(hall)
        scores_per_iteration[pad_iter]["latency"].append(lat)
        scores_per_iteration[pad_iter]["failed_instructions"].append(fail_cnt)

# Create DataFrame for plotting
rows = []
for iter_num, metrics in scores_per_iteration.items():
    for val in metrics["residual"]:
        rows.append({"Iteration": iter_num, "Metric": "Residual Error", "Value": val})
    for val in metrics["ia"]:
        rows.append({"Iteration": iter_num, "Metric": "Instruction Adherence", "Value": val})
    for val in metrics["halluc"]:
        rows.append({"Iteration": iter_num, "Metric": "Hallucination", "Value": val})
    for val in metrics["latency"]:
        rows.append({"Iteration": iter_num, "Metric": "Latency (ms)", "Value": val})
    for val in metrics["failed_instructions"]:
        rows.append({"Iteration": iter_num, "Metric": "Failed Instructions", "Value": val})

df = pd.DataFrame(rows)

# Plotting
for metric_name in df["Metric"].unique():
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[df["Metric"] == metric_name], x="Iteration", y="Value", width=0.6)
    sns.lineplot(data=df[df["Metric"] == metric_name], x="Iteration", y="Value", estimator="mean", label="Mean", marker="o", color="red")
    plt.title(f"{metric_name} by Iteration")
    plt.tight_layout()
    plt.show()
