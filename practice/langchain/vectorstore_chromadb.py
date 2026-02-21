#chroma 
#pip install langchain-chroma chromadb
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# 1) Create embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2) Your text data
texts = [
    "I work on AI projects.",
    "I will become a proper AI engineer",
    "I will create a good product",
    "my name sathya",
    "Traveling now"

]
# 3) Build a Chroma vector store
vectorstore = Chroma.from_texts(texts=texts, embedding=embeddings, persist_directory="my_chroma_vector", collection_name="example_collection")

# Add embeded into that folder
# vectorstore.persist()
# # load it from that folder
loaded = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./my_chroma_vector"
)
# 4) Query
#results = vectorstore.similarity_search("What do I want to become?")
print(vectorstore.similarity_search("what is my job", k=2))
