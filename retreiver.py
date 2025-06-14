from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding



policies_path = "./db/llamaindex_store_policies"
standards_path="./db/llamaindex_store_standards"# Path to your storage directory

policies_context = StorageContext.from_defaults(persist_dir=policies_path)
standards_context = StorageContext.from_defaults(persist_dir=standards_path)



embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-m3"
)  

polices_index = load_index_from_storage(policies_context, embed_model=embed_model)
standards_index = load_index_from_storage(standards_context, embed_model=embed_model)

polices_retreiver = VectorIndexRetriever(
    index=polices_index,
    similarity_top_k=20,  # Number of most relevant chunks to retrieve
)
standards_retreiver = VectorIndexRetriever(
    index=standards_index,
    similarity_top_k=20,  # Number of most relevant chunks to retrieve
)

# Use retriever to get additional relevant information
#    retrieved_nodes = retriever.retrieve(document)
#    additional_context = "\n\n".join([node.text for node in retrieved_nodes])