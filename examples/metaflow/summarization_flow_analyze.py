from metaflow import FlowSpec, step
from langchain_community.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from aimon import AnalyzeProd, Application, Model
import os

analyze_prod = AnalyzeProd(
    Application("my_first_metaflow_llm_app"),
    Model("my_best_model", "Llama3"),
    values_returned=["context", "generated_text"],
)


class SummarizeFlowWithAnalyze(FlowSpec):
    
    @step
    def start(self):
        # Load your document here
        self.document = """
        Your document text goes here. Replace this text with the actual content you want to summarize.
        """
        
        aimon_res, summary = self.summarize(self.document)
        
        # Print the summary
        print("Summary:")
        print(summary)

        # Print the summary
        print("Aimon Res:")
        print(aimon_res)

        self.next(self.end)

    @analyze_prod
    def summarize(self, context):
        # Split the source text
        text_splitter = CharacterTextSplitter()
        texts = text_splitter.split_text(context)

        # Create Document objects for the texts
        docs = [Document(page_content=t) for t in texts[:3]]

        openai_key = os.getenv("OPENAI_KEY")

        # Initialize the OpenAI model
        llm = OpenAI(temperature=0, api_key=openai_key)

        # Create the summarization chain
        summarize_chain = load_summarize_chain(llm)

        # Summarize the document
        return context, summarize_chain.run(docs)

    @step
    def end(self):
        print("Flow completed.")

if __name__ == "__main__":
    SummarizeFlowWithAnalyze()

