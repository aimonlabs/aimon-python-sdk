import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.readers.web import SimpleWebPageReader
from aimon import Client
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
st.set_page_config(page_title="AIMon Chatbot Demo", page_icon="🦙", layout="centered", initial_sidebar_state="auto",
                   menu_items=None)


@st.cache_resource(show_spinner=False)
def load_data():
    index_file_dir = "./data/PG"
    index_file_persisted = index_file_dir + "/persisted"
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        system_prompt="""You are an expert on 
                        answering questions on Essays and your 
                        job is to answer questions related to this domain. Your answers should be based on 
                        facts – do not hallucinate features.""",
    )
    Settings.chunk_size = 256
    Settings.chunk_overlap = 50
    if os.path.exists(index_file_persisted):
        logging.info("Loading index from disk...")
        # Rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=index_file_persisted)
        # Load index
        rindex = load_index_from_storage(storage_context)
        return rindex
    logging.info("Creating index from documents...")
    docs = SimpleWebPageReader(html_to_text=True).load_data(["http://paulgraham.com/worked.html"])

    rindex = VectorStoreIndex.from_documents(docs)
    # Save the newly created index to disk
    rindex.storage_context.persist(persist_dir=index_file_persisted)
    logging.info("Finished creating index and saving to disk...")
    return rindex


def get_source_docs(chat_response):
    contexts = []
    relevance_scores = []
    if hasattr(chat_response, 'source_nodes'):
        for node in chat_response.source_nodes:
            if hasattr(node, 'node') and hasattr(node.node, 'text') and hasattr(node,
                                                                                'score') and node.score is not None:
                contexts.append(node.node.text)
                relevance_scores.append(node.score)
            elif hasattr(node, 'text') and hasattr(node, 'score') and node.score is not None:
                contexts.append(node.text)
                relevance_scores.append(node.score)
            else:
                logging.info("Node does not have required attributes.")
    else:
        logging.info("No source_nodes attribute found in the chat response.")
    return contexts, relevance_scores


def split_into_paragraphs(text):
    import re
    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace single newlines within paragraphs with a space
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Split by double newlines
    paragraphs = text.split('\n\n')
    return paragraphs


def chat(ctx_extraction_func, usr_prompt):
    response = st.session_state.chat_engine.chat(usr_prompt)
    contexts, relevance_scores = ctx_extraction_func(response)
    message = {"role": "assistant", "content": response.response}
    return message, response

def execute():
    openai_api_key = st.secrets.openai_key
    aimon_api_key = st.secrets.aimon_api_key
    email = st.secrets.aimon_email

    openai.api_key = openai_api_key
    st.title("Ask questions on Paul Graham's Work Experience")

    if "messages" not in st.session_state.keys():  # Initialize the chat messages history
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ask me a question about Paul Graham's work experience",
            }
        ]

    index = load_data()
    memory = ChatMemoryBuffer.from_defaults(token_limit=1200)
    aimon_client = Client(aimon_api_key)

    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memory,
            context_prompt=(
                "You are a chatbot, able to answer questions on an essay about Paul Graham's Work experience."
                "Here are the relevant documents for the context:\n"
                "{context_str}"
                "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
            ),
            verbose=False,
            similarity_top_k=4,
        )

    cprompt = st.chat_input(
        "Example: Where did Paul Graham Work? || Do not answer any questions outside of the provided context documents.")
    if cprompt:  # Prompt for user input and save to chat history
        logging.info("Prompt: %s", cprompt)
        split_text = cprompt.split("||")
        logging.info("text: %s", split_text)
        usr_prompt, instructions = split_text[0], split_text[1] if len(split_text) > 1 else None
        logging.info("Prompt: %s, Ins: %s", usr_prompt, instructions)
        st.session_state.messages.append({"role": "user", "content": usr_prompt, "instructions": instructions})
    else:
        usr_prompt = None
        instructions = None

    for message in st.session_state.messages:  # Write message history to UI
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "aimon_response" in message:
                combined_json = {"AIMon Response": message["aimon_response"], "context": message["context"]}
                st.json(combined_json, expanded=False)

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            logging.info("Adding a message")
            if usr_prompt:
                message, response = chat(get_source_docs, usr_prompt)

                contexts, relevance_scores = get_source_docs(response)
                combined_context = "\n".join(contexts) if contexts else ""
                # Call AIMon
                data_to_send = [{
                    "context": combined_context,
                    "generated_text": response.response,
                    "instructions": "\n".join(instructions if instructions else []).strip()
                }]

                config = Config({
                    'hallucination': 'default'
                })
                if instructions:
                    config.detectors['instruction_adherence'] = {'detector_name': 'default'}

                am_res = aimon_client.detect(data_to_send, config=config)[0]
                st.write(response.response)
                if am_res and len(am_res) > 0:
                    st.json(am_res)
                    st.json({"context": combined_context}, expanded=False)
                    message['aimon_response'] = am_res
                    message['context'] = {"text": combined_context}
                # Add response to message history
                st.session_state.messages.append(message)


execute()
