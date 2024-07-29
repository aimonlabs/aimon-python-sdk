# AIMon Metaflow Demo

This is a simple Metaflow flow that generates a summary of an input document.
It uses AIMon to check the quality of the generated summary.
The summarizer is built using Langchain. 

## Setup

### Installation

Install the required packages from the `requirements.txt` file specified in this directory.

```bash
pip install -r requirements.txt
```

### API Keys

You will need to specify AIMon and OpenAI API keys as part of their respective environment variables. 

```bash
export OPENAI_KEY=YOUR_OPENAI_API
export AIMON_API_KEY=YOUR_AIMON_API
```

### Running the flow

The flow can be run using the following command:

```bash
python summarization_flow.py run
```


