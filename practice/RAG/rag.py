#Self RAG
#task in self RAG
"""
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
loader = TextLoader("my_notes.txt")
docs = loader.load()
splitter = CharacterTextSplitter (chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents (chunks, embeddings)
retriever = vectorstore.as_retriever()
llm = ChatOpenAI (temperature=0)
qa = RetrievalQA.from_chain_type (llm = llm , retriever=retriever)
def self_rag_query(question):
    print("First attempt without retrieval:")
    first_answer = llm.predict(f"Q: {question}\nA:")
    if "I'm not sure in first_answer or len(first_answer) < 30":
        print("Low confidence. Retrieving context and trying again...")
        improved_answer = qa.run(question)
        return improved_answer
    else:
        return first_answer
response = self_rag_query("What is the capital of France?")
print("\nFinal Answer:", response)
"""

#CorrectiveRAG
#corrective rag (answer, then check docs)
#task in corrective rag
"""
def corrective_rag(question):
    first_guess = llm.predict(f"Try to answer: {question}")
    docs = [Document(page_content="The largest cat is a liger.")]
    m
    db = FAISS.from_documents(docs, embedding)
    qa_chain = RetrievalQA.from_chain_type ( llm = llm , retriever=db.as_retriever())
    correction = qa_chain.run(question)
    return f"Original answer: {first_guess}\nCorrected using documents: {correction}"
print(corrective_rag("What is the largest cat?"))
"""

#FusionRAG
#Fusion rag (combine multiple doc)
#task in Fusion rag
"""
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document

docs = [
    Document(page_content="The sun is a star."),
    Document(page_content="The sun provides heat and light."),
    Document(page_content="It rises in the east.")
]
embedding = OpenAIEmbeddings()
db = FAISS.from_documents (docs, embedding)
fusion_rag_chain = RetrievalQA.from_chain_type(
    llm = llm ,
    retriever=db.as_retriever(),
    return_source_documents=False
)

print(fusion_rag_chain.run("Tell me about the sun"))
"""

#AdvancedRAG
#Advanced rag (guess, retrive reasoning correct)
#task in Advanced rag
"""
def advanced_rag(question):
    guess_topic = llm.predict(f"What is the main topic of: {question}?")
    docs = [
        Document (page_content="Mercury is the closest planet to the sun.")
        Document(page_content="Venus is the second planet."),
        Document (page_content="Earth is our home."),
        Document(page_content="Mars is the red planet.")
    ]
    db = FAISS.from_documents (docs, embedding)
    qa_chain = RetrievalQA.from_chain_type (llm = llm , retriever=db.as_retriever())
    result = qa_chain.run(question)
    return f"Topic: {guess_topic}\nAnswer: {result}"
print(advanced_rag("Tell me about the planets in the solar system."))
"""

#speculativeRAG
#speculative rag (guess what to retrive first)
#task in Advanced rag

def speculative_rag(question):
    guess_prompt = PromptTemplate.from_template("Extract keyword for: {question}")
    guess_chain = LLMChain(llm=llm, prompt=guess_prompt)
    keyword = guess_chain.run(question)
    I
    docs = [Document (page_content="An elephant is the largest land animal.")]
    db = FAISS.from_documents (docs, embedding)
    retriever = db.as_retriever (search_kwargs={"k": 1})
    qa_chain = RetrievalQA.from_chain_type ( l1m = llm , retriever=retriever)
    return qa_chain.run(f"What do you know about {keyword}?")
print(speculative_rag("What is the largest land animal?"))