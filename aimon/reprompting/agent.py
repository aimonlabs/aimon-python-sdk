import json
from together import Together

class Agent:
    def __init__(self):
        self.client = Together(api_key="8b6726e35a842117f91077ca78fc69e1ee285c998592fd8356bd4123a63378a1")

    def get_response(self, llm_num, prompt):
        if llm_num == 1:
            return self.mistral_response(prompt)
        return "Unsupported Model Number"

    def get_model_name(self, llm_num):
        if llm_num == 1:
            return "mistralai/Mistral-7B-Instruct-v0.2"
        return "Unknown Model"

    def mistral_response(self, prompt):
        response = self.client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        output = ""
        for token in response:
            if hasattr(token, 'choices'):
                delta = token.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    output += delta.content
        return output