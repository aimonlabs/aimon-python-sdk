# Summarization

This is a simple streamlit based Langchain Summarization application with an inline AIMon detector.

## Setup

Make sure you have the AIMon API key which can be obtained by signing up on the AIMon website.

### Installation

Install the required packages from the `requirements.txt` file specified in this directory.

```bash
pip install -r requirements.txt
```

### API Keys

You will need to specify AIMon and OpenAI API keys in a `secrets.toml` file inside the 
`.streamlit` directory. 

```toml
openai_key=YOUR_OPENAI_API_KEY
aimon_api_key=YOUR_AIMON_API_KEY
```

### Running the Summarization App

The summarization app is a streamlit app. You can run it using this command:

```bash
streamlit run langchain_summarization_app.py
```
