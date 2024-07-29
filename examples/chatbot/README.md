# AIMon Chatbot Demo

This is a simple chatbot demo that uses AIMon to check responses to user queries. 
The chatbot is built using LLamaIndex. 

## Setup

### Installation

Install the required packages from the `requirements.txt` file specified in this directory.

```bash
pip install -r requirements.txt
```

### API Keys

You will need to specify AIMon and OpenAI API keys in a `secrets.toml` file inside the 
`.streamlit` directory. 

```toml
openai_key=YOUR_OPENAI_API
aimon_api_key=YOUR_AIMON_API
```

### Running the Chatbot

The chatbot is a streamlit app. You can run it using this command:

```bash
streamlit run chatbot.py
```


