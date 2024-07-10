import streamlit as st
from chatbot import chatbot, extract_instructions
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
            (chatbot_response, hallucination_score, toxicity,conciseness, adherence_details, completeness,detection_response) = chatbot(user_query, instructions, openai_api_key, api_key)
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

            st.header('Aimon Rely - Hallucination Detector Response')
            if 'hallucination' in detection_response:
                st.json(detection_response['hallucination'])
            else:
                st.write("Hallucination data is not available.")

            st.header('Aimon Rely - Model Conciseness Detector Response')
            if 'conciseness' in detection_response:
                st.json(detection_response['conciseness'])
            else:
                st.write("Conciseness data is not available.")

            st.header('Aimon Rely - Model Completeness Detector Response')
            if 'completeness' in detection_response:
                st.json(detection_response['completeness'])
            else:
                st.write("Completeness data is not available.")    
            
            st.header('Aimon Rely - Toxicity Detector Response')
            if 'toxicity' in detection_response:
                st.json(detection_response['toxicity']['results'])
            else:
                st.write("Toxicity data is not available.")
            
            st.header('Adherence Detector Response')
            if 'instruction_adherence' in detection_response:
                st.json(detection_response['instruction_adherence'])
            else:
                st.write("Instruction adherence data is not available.")


