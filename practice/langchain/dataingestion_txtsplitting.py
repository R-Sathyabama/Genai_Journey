##txt data ingestion
"""
#pip install langchain_community
from langchain_community.document_loaders import TextLoader
#pip install TextLoader
text = TextLoader("notes.txt")
print(text.load())

"""

##pdf data ingestion
"""
#pip install pypdf pymupdf
from langchain_community.document_loaders import PyPDFLoader
pdf = PyPDFLoader("sathiya.pdf")
print(pdf.load())

"""


##website data ingestion

"""
#pip install bs4(butterscope)
from langchain_community.document_loaders import WebBaseLoader
web = WebBaseLoader(web_path = "https://fullstackdeeplearning.com/")
print(web.load())

"""



##researchpaper data ingestion

"""
#pip install arxiv
from langchain_community.document_loaders import ArxivLoader
a = ArxivLoader(query = "2307.06435")
print(a.load())

"""

##wikipedia data ingestion
"""
#pip install TextLoader
from langchain_community.document_loaders import WikipediaLoader
a = WikipediaLoader(query = "AI Agents", load_max_docs=3)
print(a.load())

"""

##Test Splitting


from langchain_community.document_loaders import PyPDFLoader
pdf = PyPDFLoader("sathiya.pdf")
b = pdf.load()
a = "/n".join([doc.page_content for doc in b])

"""
#CharacterTextSplitting
from langchain_text_splitters import CharacterTextSplitter
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", chunk_size=100, chunk_overlap=0
)
texts = text_splitter.split_text(a)
print(texts)
"""

#RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=1)
texts = text_splitter.split_text(a)

print(texts)