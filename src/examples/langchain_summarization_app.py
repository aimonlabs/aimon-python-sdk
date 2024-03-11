# Run these steps running the streamlit application
# Step 1: python3 setup.py install --user
# Step 2: pip install -r requirements.txt

#
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain

from aimon_rely_client.simple_client import SimpleAimonRelyClient

API_KEY = "YOUR API KEY HERE"

# Streamlit app
st.title('LangChain Text Summarizer')

# Get OpenAI API key and source text input
openai_api_key = st.text_input("OpenAI API Key", type="password")
source_text = st.text_area("Source Text", height=200)

aimon_rely_client = SimpleAimonRelyClient(API_KEY)

# Check if the 'Summarize' button is clicked
if st.button("Summarize"):
    # Validate inputs
    if not openai_api_key.strip() or not source_text.strip():
        st.write(f"Please complete the missing fields.")
    else:
        try:
            # Split the source text
            text_splitter = CharacterTextSplitter()
            texts = text_splitter.split_text(source_text)

            # Create Document objects for the texts
            docs = [Document(page_content=t) for t in texts[:3]]

            # Initialize the OpenAI module, load and run the summarize chain
            llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
            chain = load_summarize_chain(llm, chain_type="map_reduce")
            summary = chain.run(docs)

            # Display summary
            st.header('Summary')
            st.write(summary)

            # Call Aimon Rely and render response
            ar_response = aimon_rely_client.detect([
                {
                    "context": source_text,
                    "generated_text": summary
                }
            ])

            # You could perform any action based on this reponse here
            # ....

            # Display the Aimon Rely response
            st.header('Aimon Rely - Hallucination Detector Response')
            st.json(ar_response)

        except Exception as e:
            st.write(f"An error occurred: {e}")
