## AIMon - LlamaIndex 


## Function to generate nodes (from documents) with embeddings and metadata
def generate_embeddings_for_docs(documents, embedding_model):

    # Using the LlamaIndex SentenceSplitter, parse the documents into text chunks.

    from llama_index.core.node_parser import SentenceSplitter

    text_parser = SentenceSplitter()

    text_chunks = []
    doc_idxs = []
    for doc_idx, doc in enumerate(documents):
        cur_text_chunks = text_parser.split_text(doc.text)
        text_chunks.extend(cur_text_chunks)
        doc_idxs.extend([doc_idx] * len(cur_text_chunks))

    ## Construct nodes from the text chunks.

    from llama_index.core.schema import TextNode

    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(text=text_chunk)
        src_doc = documents[doc_idxs[idx]]
        node.metadata = src_doc.metadata
        nodes.append(node)

    ## Generate embeddings for each TextNode.

    for node in nodes:
        node_embedding = embedding_model.get_text_embedding(
            node.get_content(metadata_mode="all"))
        node.embedding = node_embedding

    return nodes


## Function to build index
def build_index(nodes):
    ## Can add logic/support for more vector stores in the future
    from llama_index.core import VectorStoreIndex
    index = VectorStoreIndex(nodes)
    return index


## Function to build retriever
def build_retriever(index, similarity_top_k=5):
    from llama_index.core.retrievers import VectorIndexRetriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=similarity_top_k)
    return retriever


## Function to build a query engine and get LLM response
def get_response(user_query, retriever, llm):
    from llama_index.core.query_engine import RetrieverQueryEngine
    query_engine = RetrieverQueryEngine.from_args(retriever, llm)
    response = query_engine.query(user_query)
    return response