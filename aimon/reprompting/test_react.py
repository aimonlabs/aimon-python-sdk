
from coordinator import ReactConfig, Coordinator
from reprompter import Reprompter
from agent import Agent
import sys
import os
import json
from dataclasses import asdict
from pprint import pprint
import requests
import json


config = ReactConfig(publish=True, max_attempts=3,aimon_api_key="998e211045c1d9e5b1fc0fa9e9e001be684596d8d529952c088eb1627480529c")
reprom = Reprompter()
agent = Agent()
coordinator = Coordinator(llm_app=None, react_configuration=config, context_extractor=None, reprompter=reprom,agent=agent)

context = """SecureCloud offers encrypted file storage with two-factor authentication and regular security audits to protect user data."""

user_query = "How does SecureCloud keep my files safe?"
user_instructions = [
    "Be concise: 2 sentences max.",
    "Use informal language.",
    "Make it rhyme slightly if possible."
]

coordinator.coordinate(1,context, user_query, user_instructions)
if False:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": user_query,
    }, stream=True)

    output = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            output += data.get("response", "")
    print(output)

    # using hardcoded context, query, etc. and outputting AIMON's IA and HDM2 model's evaluation of the output
    payload = coordinator.create_payload(context, user_query, user_instructions,output)
    result = coordinator.detect_aimon_response(user_query,user_instructions)
    print(result)

    print("extracting key info from result")

    # Top-level scores
    print("Hallucinated:", result.hallucination["is_hallucinated"])
    print("Hallucination Score:", result.hallucination["score"])
    print("Instruction Adherence Score:", result.instruction_adherence["score"])

    # Show top hallucinated sentence
    if result.hallucination["context_hallucinations"]:
        top_hallucination = max(result.hallucination["context_hallucinations"], key=lambda h: h["score"])
        print("\nTop Hallucinated Text:")
        print(f"- Score: {top_hallucination['score']}")
        print(f"- Text: {top_hallucination['text']}")

    ## Show all instruction compliance checks
    print("\nInstruction Adherence:")
    for i in result.instruction_adherence["instructions_list"]:
        status = "✅" if i["label"] else "❌"
        print(f"{status} {i['instruction']} (score: {i['follow_probability']:.3f})")

    cp = coordinator.reprompter.create_corrective_prompt(result,payload)
    print("create corrective prompt")
    print(cp)




