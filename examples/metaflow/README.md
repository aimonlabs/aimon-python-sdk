# AIMon Metaflow Demo

This repo contains two simple Metaflow flows that generates a summary of an input document.
It uses AIMon's `analyze` and `detect` decorators to check the quality of the generated summary.
The summarizer is built using Langchain. 

## Setup

Make sure you have the AIMon API key which can be obtained by signing up on the AIMon website.

### Installation

Install the required packages from the `requirements.txt` file specified in this directory.

```bash
pip install -r requirements.txt
```

### API Keys

You will need to specify AIMon and OpenAI API keys as part of their respective environment variables. 

```bash
export OPENAI_KEY=YOUR_OPENAI_API_KEY
export AIMON_API_KEY=YOUR_AIMON_API_KEY
```

### Running the flow

The flow can be run using the following command:

```bash
python summarization_flow.py run
```


