import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain

from aimon import Detect

# Streamlit app
st.title('LangChain Text Summarizer')

# Get OpenAI API key and source text input
openai_api_key = st.secrets.openai_key
aimon_api_key = st.secrets.aimon_api_key
source_text = st.text_area("Source Text", height=200)

config = {"hallucination": {"detector_name": "default"},
          "conciseness": {"detector_name": "default"},
          "completeness": {"detector_name": "default"},
          "toxicity": {"detector_name": "default"}
          }
detect = Detect(['context', 'generated_text'], api_key=aimon_api_key, config=config)


@detect
def summarize():
    # Split the source text
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(source_text)
    # Create Document objects for the texts
    docs = [Document(page_content=t) for t in texts[:3]]
    # Initialize the OpenAI module, load and run the summarize chain
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    doc_summary = chain.run(docs)
    return source_text, doc_summary


# Check if the 'Summarize' button is clicked
if st.button("Summarize"):
    # Validate inputs
    if not openai_api_key.strip() or not aimon_api_key.strip():
        st.write("Please provide the OpenAI and AIMon API keys in the .streamlit/secrets.toml file.")
    if not source_text.strip():
        st.write(f"Please complete the missing fields.")
    else:
        try:
            context, summary, aimon_res = summarize()
            # Display summary
            st.header('Summary')
            st.write(summary)

            # You could perform any action based on the AIMon response (aimon_res) here
            # ....

            # Display the Aimon Rely response
            st.header('Aimon Rely - Hallucination Detector Response')
            st.json(aimon_res.hallucination)

            st.header('Aimon Rely - Conciseness Detector Response')
            st.json(aimon_res.conciseness)

            st.header('Aimon Rely - Completeness Detector Response')
            st.json(aimon_res.completeness)

            st.header('Aimon Rely - Toxicity Detector Response')
            st.json(aimon_res.toxicity)

        except Exception as e:
            st.write(f"An error occurred: {e}")
