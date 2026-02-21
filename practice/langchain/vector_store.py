#FAISS  is one of the method in vector store it is Fast, lightweight, local  store
#pip install fiass-cpu

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
text = [
    "I work on AI projects.",
    "I will become Proper AI engineer",
    "I will create good product"
]
embedtext = HuggingFaceEmbeddings(model_name="all-MiniLm-L6-v2")
vectorstore=FAISS.from_texts(text,embedtext)
vectorstore.save_local("my_faiss_vector")
results = vectorstore.similarity_search("AI engineer", k=2)
for r in results:
    print(r.page_content)


