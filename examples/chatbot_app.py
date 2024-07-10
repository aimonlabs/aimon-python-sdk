import streamlit as st
from chatbot import chatbot, extract_instructions
from aimon.client import Client
from aimon import Config
import os
import json

email = os.getenv('EMAIL')

st.header("Chatbot")

st.markdown("""
    <style>
    .message-box {
        max-width: 40%;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #D3D3D3;
        text-align: left;
    }
    .bot-message {
        background-color: #D3D3D3;
        text-align: right;
        margin-left: auto;
    }
    </style>
    """, unsafe_allow_html=True)

openai_api_key = st.text_input("Enter OpenAI API Key:", type="password")
api_key = st.text_input("Enter API Key:", type="password")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f"<div class='message-box user-message'><strong>User:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-box bot-message'><strong>Chatbot:</strong> {message['content']}</div>", unsafe_allow_html=True)

user_query = st.text_area("User Query", height=100)
system_prompt = st.text_area("System Prompt", height=100)


def validate_payload(payload):
    expected_structure = {
        "context": str,
        "generated_text": str,
        "instructions": str
    }

    for key, expected_type in expected_structure.items():
        if key not in payload or not isinstance(payload[key], expected_type):
            st.write(f"Key: {key}, Expected Type: {expected_type}")
            return False

    return True

if st.button("Chat with Chatbot"):
    if not user_query.strip():
        st.write("Please enter a user query.")
    elif not openai_api_key.strip() or not api_key.strip():
        st.write("Please enter both API keys.")
    elif not system_prompt.strip():
        st.write("Please enter a system prompt.")
    else:
        user_message = {"role": "user", "content": user_query}
        st.session_state.conversation.append(user_message)

        instructions = extract_instructions(system_prompt)
        st.session_state["system_prompt"] = system_prompt

        try:
            chatbot_response, hallucination_score, toxicity, conciseness, adherence_details, completeness = chatbot(user_query, instructions, openai_api_key, api_key)
        except Exception as e:
            st.write(f"Error occurred: {e}")
            chatbot_response = "Error occurred while processing your request."

        if chatbot_response == "Error occurred while processing your request.":
            st.write(chatbot_response)
        else:
            st.session_state['hallucination_score'] = hallucination_score
            st.session_state['toxicity'] = toxicity
            st.session_state['conciseness'] = conciseness
            st.session_state['completeness'] = completeness
            st.session_state['adherence_details'] = adherence_details

            bot_message = {"role": "bot", "content": chatbot_response}
            st.session_state.conversation.append(bot_message)
            st.markdown(f"<div class='message-box bot-message'><strong>Chatbot:</strong> {chatbot_response}</div>", unsafe_allow_html=True)

            try:
                context_str = "\n".join([msg["content"] for msg in st.session_state.conversation if msg["role"] == "user"])
                payload = {
                    "context": context_str,
                    "generated_text": chatbot_response,
                    "instructions": "\n".join(instructions)
                }

                if validate_payload(payload):
                    client = Client(api_key=api_key, email=email)
                    ar_response = client.detect([payload], config=Config(
                        {'hallucination': 'default', 'conciseness': 'default', 'completeness': 'default', 'toxicity': 'default', 'instruction_adherence': 'default'}))
                    
                    st.header('Aimon Rely - Hallucination Detector Response')
                    st.json(ar_response[0].get('hallucination', {}))
                    
                    st.header('Aimon Rely - Model Conciseness Detector Response')
                    if 'conciseness' in ar_response[0]:
                        st.json(ar_response[0]['conciseness'])
                    else:
                        st.write("Quality metrics data is not available.")

                    st.header('Aimon Rely - Model Completeness Detector Response')
                    if 'completeness' in ar_response[0]:
                        st.json(ar_response[0]['completeness'])
                    else:
                        st.write("Quality metrics data is not available.")    
                    
                    st.header('Aimon Rely - Toxicity Detector Response')
                    if 'toxicity' in ar_response[0]:
                        st.json(ar_response[0]['toxicity']['results'])
                    else:
                        st.write("Toxicity data is not available.")
                    
                    st.header('Adherence Detector Response')
                    if 'instruction_adherence' in ar_response[0]:
                        st.json(ar_response[0]['instruction_adherence'])
                    else:
                        st.write("Instruction adherence data is not available.")
                else:
                    st.write("Invalid payload structure")
            except Exception as e:
                st.write(f"Exception: {e}")
                if 'response' in locals():
                    st.write(f"Response content: {response.content}")
