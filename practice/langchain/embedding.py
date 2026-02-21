#Openai
"""
from langchain.embeddings import OpenAIEmbeddings
openai_embed = OpenAIEmbeddings(openai_api_key="")
textembed = "this isone of the most wonderful gen ai process"
embeded =  openai_embed.embed_query(textembed)
print(embeded[:5])

# do embedding using grak
"""

#Hugging face
"""
from langchain_community.embeddings import HuggingFaceEmbeddings
hfembed = HuggingFaceEmbeddings(model_name="all-MiniLm-L6-v2")
texthfembed = "this isone of the most wonderful gen ai process"
hfembeded =  hfembed.embed_query(texthfembed)
print(hfembeded[:5])

"""
##Groqtask

#export GROQ_API_KEY="xxx"
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# 1) Embeddings
hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
text = "this is one of the most wonderful gen ai process"
hf_embedding = hf.embed_query(text)
print("HuggingFace embedding (first 5):", hf_embedding[:5])

# 2) Groq LLM
llm = ChatGroq(
    model="qwen/qwen3-32b",   # replace with a Groq-supported model
    temperature=0.0,
)
response = llm.invoke([
    ("system", "You are an assistant."),
    ("human", "Explain how embeddings work in LangChain."),
])
print("Groq LLM response:", response.content)
