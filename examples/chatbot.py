import os
import openai
import nest_asyncio
import certifi
import nltk
from pathlib import Path
from llama_index.readers.file import UnstructuredReader
from llama_index.core import VectorStoreIndex, StorageContext, Settings, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.agent.openai import OpenAIAgent
from aimon.client import Client
import streamlit as st
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
import requests
import json
from botocore.exceptions import ClientError
import boto3
from aimon import Config
import logging
import time
import numpy as np

load_dotenv()

email = os.getenv('EMAIL')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)

nest_asyncio.apply()
os.environ['SSL_CERT_FILE'] = certifi.where()

# Download UBER dataset
os.system("mkdir -p data")
os.system('wget "https://www.dropbox.com/s/948jr9cfs7fgj99/UBER.zip?dl=1" -O data/UBER.zip')
os.system("unzip -o data/UBER.zip -d data")
nltk.download('averaged_perceptron_tagger')

# Load UBER documents
years = [2022, 2021, 2020, 2019]
loader = UnstructuredReader()
doc_set = {}
all_docs = []
index_set = {}

for year in years:
    year_docs = loader.load_data(file=Path(f"./data/UBER/UBER_{year}.html"), split_documents=False)
    # Insert year metadata into each document
    for d in year_docs:
        d.metadata = {"year": year}
    doc_set[year] = year_docs
    all_docs.extend(year_docs)

Settings.chunk_size = 512
Settings.chunk_overlap = 64
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Initialize simple vector indices
index_set = {}
for year in years:
    storage_context = StorageContext.from_defaults()
    cur_index = VectorStoreIndex.from_documents(
        doc_set[year],
        storage_context=storage_context,
    )
    index_set[year] = cur_index
    storage_context.persist(persist_dir=f"./storage/{year}")

individual_query_engine_tools = [
    QueryEngineTool(
        query_engine=index_set[year].as_query_engine(),
        metadata=ToolMetadata(
            name=f"vector_index_{year}",
            description=f"useful for when you want to answer queries about the {year} SEC 10-K for Uber",
        ),
    )
    for year in years
]

# Initialize SubQuestionQueryEngine
query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=individual_query_engine_tools,)

query_engine_tool = QueryEngineTool(
    query_engine=query_engine,
    metadata=ToolMetadata(
        name="sub_question_query_engine",
        description="useful for when you want to answer queries that require analyzing multiple SEC 10-K documents for Uber",
    ),
)
tools = individual_query_engine_tools + [query_engine_tool]
agent = OpenAIAgent.from_tools(tools, verbose=True)

def extract_instructions(system_prompt):
    instructions = system_prompt.split("\n")
    instructions = [instruction.strip() for instruction in instructions if instruction.strip()]
    return instructions


def validate_and_format_json(data):
    try:
        json_string = json.dumps(data)
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        raise

def chatbot(user_query, instructions, openai_api_key, api_key, email):
    openai.api_key = openai_api_key
    contexts = []
    relevance_scores = []
    input_text = f"Instructions: {instructions}\nQuery: {user_query}"

    logging.info("Sending request to OpenAI API...")
    st.write("Waiting for response from OpenAI API...")
    chat_response = agent.chat(input_text)
    logging.info("Received response from OpenAI API.")

    if hasattr(chat_response, 'source_nodes'):
        for node in chat_response.source_nodes:
            if hasattr(node, 'node') and hasattr(node.node, 'text') and hasattr(node, 'score') and node.score is not None:
                contexts.append(node.node.text)
                relevance_scores.append(node.score)
            elif hasattr(node, 'text') and hasattr(node, 'score') and node.score is not None:
                contexts.append(node.text)
                relevance_scores.append(node.score)
            else:
                logging.info("Node does not have required attributes.")
    else:
        logging.info("No source_nodes attribute found in the chat response.")

    sorted_contexts = [context for _, context in sorted(zip(relevance_scores, contexts), reverse=True)]
    top_contexts = sorted_contexts[:20]

    if not top_contexts:
        logging.info("No contexts found.")

    else:
        combined_context = "\n".join(top_contexts)

    data_to_send = validate_and_format_json([{
        "context": combined_context,
        "generated_text": chat_response.response,
        "instructions": "\n".join(instructions)
    }])

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logging.info(f"Sending data to Aimon API for detection (attempt {attempt + 1})...")
            client = Client(api_key=api_key, email=email)

            config = Config({
                'hallucination': 'default',
                'conciseness': 'default',
                'completeness': 'default',
                'toxicity': 'default',
                'instruction_adherence': 'default'
            })
            st.write(f"Waiting for response from Aimon API...")
            response = client.detect(data_to_send, config=config)[0]

            logging.info("Received response from Aimon API.")
            break
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout occurred while processing your request: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return "Error occurred while processing your request due to timeout.", None, None, None, None, None, None
        except requests.exceptions.RequestException as e:
            logging.error(f"RequestException occurred: {e}")
            return "Error occurred while processing your request due to a request exception.", None, None, None, None, None, None
        except Exception as e:
            logging.error(f"Error occurred while processing your request: {e}")
            return "Error occurred while processing your request.", None, None, None, None, None, None

    hallucination_score = response.get('hallucination', {}).get('score', None)
    toxicity = response.get('toxicity', None)
    conciseness = response.get('conciseness', None)
    completeness = response.get('completeness', None)
    adherence_details = response.get('instruction_adherence', [])

    return (
        str(chat_response.response),
        hallucination_score,
        toxicity,
        conciseness,
        adherence_details,
        completeness,
        response 
    )
