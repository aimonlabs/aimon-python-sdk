import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.readers.web import SimpleWebPageReader
from aimon import Detect
from aimon import AuthenticationError
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
st.set_page_config(page_title="AIMon Chatbot Demo", layout="centered", initial_sidebar_state="auto",
                   menu_items=None)

aimon_config = {'hallucination': {'detector_name': 'default'}, 'instruction_adherence': {'detector_name': 'default'}}
detect = Detect(values_returned=['context', 'user_query', 'instructions', 'generated_text'], api_key=st.secrets.aimon_api_key, config=aimon_config)


@st.cache_resource(show_spinner=False)
def load_data():
    index_file_dir = "./data/PG"
    index_file_persisted = index_file_dir + "/persisted"
    logging.info("Creating OpenAI LLM...")
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        system_prompt="""You are an expert on 
                        answering questions on Essays and your 
                        job is to answer questions related to this domain. Your answers should be based on 
                        facts – do not hallucinate features.""",
    )
    logging.info("Finished creating OpenAI LLM...")
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


@detect
def am_chat(usr_prompt, instructions):
    response = st.session_state.chat_engine.chat(usr_prompt)
    context = get_source_docs(response)
    return context, usr_prompt, instructions, response.response


def execute():
    openai_api_key = st.secrets.openai_key

    openai.api_key = openai_api_key
    instructions = st.text_input(
        "Instructions for the chatbot. Ex: Answer the user's question in a professional tone.")
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

    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memory,
            context_prompt=(
                "You are a chatbot, able to answer questions on an essay about Paul Graham's Work experience."
                "Here are the relevant documents for the context:\n"
                "{context_str}"
                "\nInstruction: Use the previous chat history, or the context above, to interact and help the user. " +
                "{}".format(instructions if instructions else "")
            ),
            verbose=False,
            similarity_top_k=4,
        )

    if cprompt := st.chat_input("Example: Where did Paul Graham Work?"):
        st.session_state.messages.append({"role": "user", "content": cprompt})

    for message in st.session_state.messages:  # Write message history to UI
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "aimon_response" in message:
                combined_json = {"AIMon Response": message["aimon_response"], "context": message["context"]}
                st.json(combined_json, expanded=False)

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            if cprompt:
                context, usr_prompt, instructions, response, am_res = am_chat(cprompt, instructions)
                message = {"role": "assistant", "content": response}
                am_res_json = am_res.to_json()
                st.write(response)
                if am_res_json and len(am_res_json) > 0:
                    st.json(am_res_json)
                    st.json({"context": context}, expanded=False)
                    message.update({'aimon_response': am_res_json, 'context': {"text": context}})
                # Add response to message history
                st.session_state.messages.append(message)


try:
    execute()
except AuthenticationError as e:
    st.error("Authentication error. Please check your AIMon API key.")
