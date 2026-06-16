from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv, find_dotenv
import chromadb
import os

load_dotenv(find_dotenv())
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

# rag: retrieval augmented generation
# job: store all medical reports in chromadb and let the user ask questions across all of them
# why rag and not just send everything to the llm?
# because the llm has a limit  you cant paste 10 medical reports in one message
# rag solves this by finding only the most relevant chunks and sending those to the llm
# so the llm only sees what is relevant to the question — not the whole documents

# this is the same concept from day 12 but now applied across MULTIPLE files
# day 12: one document  chromadb  ask questions
# today: multiple medical reports chromadb  ask questions across ALL of them

# embedding model: converts text chunks into vectors (numbers)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#creat a db where we stor the medical reports in it 
# chromadb client: stores all the vectors in memory
client_db = chromadb.Client()
collection = client_db.get_or_create_collection("medical_reports")

# memory store: saves chat history so the llm remembers previous question
# store dict where key=session_id(like conversation_id) and value=chat history
store={}

def get_session_history(session_id:str): #check if the session exists if not create a new one 
    if session_id not in store:
        store[session_id]=InMemoryChatMessageHistory()
    return store[session_id]


def store_reports(raw_texts: dict):
    # takes the raw texts dict from extractor filename and text
    # splits each text into chunks by line and stores them in chromadb as vectors
    # why chunks and not full text becaus chromadb finds relevant pieces not whole documents
    # smaller chunks give more precise answers when user ask a question
    print("rag: storing all reports in chromadb...")
    chunk_id = 0

    for filename, text in raw_texts.items():
        # split text into chunks each non empty line becomes one chunk
        chunks = [line.strip() for line in text.split("\n") if line.strip()]

        for chunk in chunks:
            embedding = embedding_model.embed_query(chunk)  # covert chunk to vector
            collection.add( documents=[chunk],           # original text
            embeddings=[embedding],      # vector version of the text
            ids=[f"chunk_{chunk_id}"],   # unique id for each chunck
            metadatas=[{"source": filename}])  # remembre which file this chunk came from
            chunk_id += 1
    print(f"rag: stored {chunk_id} chunks from {len(raw_texts)} files")


def ask_question(question: str) -> str:
    #  convert the user question to a vector
    question_embedding = embedding_model.embed_query(question)

    #  chromadb finds the 3 chunks whos vectors are closest to the question vector
    results = collection.query(query_embeddings=[question_embedding], n_results=3)

    # join the 3 most relevent chunks into one context string
    # results documents 0 is the list of the 3 most relevant chunks as text
    context = "\n".join(results["documents"][0])

    #  build the prompt with memory
    # the llm receives system instructions plus chat history plus relevant chunks plus user question
    prompt = ChatPromptTemplate.from_messages([
        ("system", """you are a helpful medical assistant
         answer the patient question using only the medical records provided
         if the answer is not in the records say i dont have that information
         always mention which clinic or date the information came from"""),
        ("placeholder", "{chat_history}"),  # previous messages get injected here automaticly
        ("human", "medical records:\n{context}\n\nquestion: {input}")])

    chain = prompt | llm

    # wrap chain with memory same as day 13
    # RunnableWithMessageHistory loads chat history before every message
    # and saves the new message after every responce
    conversation = RunnableWithMessageHistory(
        chain, get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history" )

    response = conversation.invoke( {"input": question, "context": context},
    config={"configurable": {"session_id": "health_chat"}})
    return response.content


# test
if __name__ == "__main__":
    test_texts = {
        "chicago_clinic_2022.txt": "Chicago Clinic March 2022 Dr Smith blood pressure 118/76 glucose 95 diagnosis healthy",
        "wellmed_2023.txt": "WellMed January 2023 Dr Jones blood pressure 145/90 glucose 112 diagnosis pre-hypertension no medication"}

    store_reports(test_texts)  # store the reports in chromadb first
    print(ask_question("what was my blood pressure at wellmed?"))
    print(ask_question("did i have any medication prescribed?"))

