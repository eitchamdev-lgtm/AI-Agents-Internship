from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from healthtrack.config import GROQ_API_KEY, LLM_MODEL, EMBED_MODEL, CHROMA_DIR
import chromadb
import hashlib


#rag : retrieval argumented generation , store all medical reports in chromadb and let the user ask questions across all of them 

#upgrades from the old rag.py:
#better chunking with overlap so sentences dont get cut in the half,
#presistent chroma db so data can survive between run (will not loose them whenn app restart )
#idempotent ingestion with hashlib so re-running dosent duplicate data

#creat llm using api and model from config file 
llm=ChatGroq(api_key=GROQ_API_KEY,model=LLM_MODEL)

#embedding model that converts texts into vectors do we can find similar 
#chuanks , the vectors are just a list of numbers that rappresent the meaning of the text 
embedding_model=HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# persistent client saves vectors to disk in CHROMA_DIR
client_db=chromadb.PersistentClient(path=str(CHROMA_DIR))

#get or create a collection named medical reports this collection is like a table in a db where we store our chunks 
collection=client_db.get_or_create_collection("medical_reports")

#overlap, the end of one chunk repeats at the start of the next this 
#prevent important context from being cut off at chunk boundries 
splitter= RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=80)#size 500 chats

# store is a dict where key=session_id and value=chat history
store={}

#now we create a function that gett the session history or create one if it dosent exists
def get_session_history(session_id:str):
    if session_id not in store:
        store[session_id]=InMemoryChatMessageHistory()
    return store[session_id]
#quick example on how this funct works: 
#_create the object history = get_session_history("user111") of the InMemoryChatMessageHistory clas
#if we didnt found user111 in store we have # store["user111"] = InMemoryChatMessageHistory()
#now store is like this: store = {"user111": <InMemoryChatMessageHistory object>}
#but this function return the value of the sessiond it so it returns:  <InMemoryChatMessageHistory object>


#now the funct that store the reports , takes raw_text from orchestrator (filename:text)
#split each text into ovelapping chunks store each chunk as a vector in chroma db 
#uses hashlib to create deterministic ids so same chunk stored twice = upsert not duplicate
#this means running the same files twice does not double the data

def store_reports(raw_texts:dict):
    print(f"rag: collection has {collection.count()} chunks before ingestion")

    for filename, text in raw_texts.items():#loop each file and its text content
        chunks=splitter.split_text(text) #split text into overlapping chunks instead of line by line 

        for i,chunk in enumerate(chunks):#loop through each chunk
            embedding=embedding_model.embed_query(chunk) #convert chunk text to a vector

            # deterministic id: same file + same chunk position + same text = same id every time
            # this is what makes it idempotent — no adding duplicates
            cid = hashlib.md5(f"{filename}:{i}:{chunk}".encode()).hexdigest()

            # upsert: if id exists update the chunk, otherwise insert it
            # this prevents duplicates when running the same file twice
            collection.upsert(ids=[cid],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"source": filename}])# remember which file this chunk came from(metadata)
    print(f"rag: collection has {collection.count()} chunks after ingestion")




#now ask question funct. answer a question using rag converts the question to a vector
#find the most similar chunks in chromadb send the chunks + question to the llm with memory returns the answer 

#now takes session_id too not only the question 
#so each user gets their own chat memory instead of sharing one
#default value keeps the old test block at the bottom working without changes
def ask_question(question:str, session_id:str="health_chat")->str: 

    question_embedding = embedding_model.embed_query(question)# convert question to vector
    results = collection.query(query_embeddings=[question_embedding], n_results=3)# find 3 most relevant chunks from all reports
    context = "\n".join(results["documents"][0])# combine the chunks into one context string
    # build the prompt with chat history
    prompt = ChatPromptTemplate.from_messages([("system", """you are a helpful medical assistant 
         answer the patient question using only the medical records provided
         if the answer is not in the records say i dont have that information
         always mention which clinic or date the information came from"""),
        ("placeholder", "{chat_history}"),  # previous messages get injected here
        ("human", "medical records:\n{context}\n\nquestion: {input}")])
    # connect prompt to llm
    chain = prompt | llm
    # wrap chain with memory so the llm remembers previous messages
    conversation = RunnableWithMessageHistory(chain, get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history")

    # invoke(the chain that have the prompt that hase in it chat history context and input) the conversation with the question and context
    

    # before: session_id was always the fixed string "health_chat", so every user
# looked up the SAME memory bucket in store[]  everyone chat got mixed together
# now: session_id comes from the function's parameter (see def ask_question above),
# which app.py fills in with each user's own unique id  so each user gets
# their own separate memory bucket instead of sharing one with everyone else
    response = conversation.invoke({"input": question, "context": context},
    config={"configurable": {"session_id": session_id}})
    return response.content

# test block runs only when executing this file directly
if __name__ == "__main__":
    from healthtrack.orchestrator import read_file
    from healthtrack.config import SAMPLE_DIR
    
    raw_texts = read_file(str(SAMPLE_DIR))# read the sample reports once
    store_reports(raw_texts)# read the sample reports once
    
    print("\nrunning store_reports again on same files...")# run store_reports again to prove idempotency
    store_reports(raw_texts)# collection.count() should be the same both times it should NOT double because upsert updates not duplicates
    print(ask_question("what was my blood pressure at wellmed?"))


# new rag uses overlap chunking persistent chromadb deterministic ids and upsert
# old rag used line chumking in memory db sequential ids and add
# new is better because it keeps context survive restart and never duplicates data