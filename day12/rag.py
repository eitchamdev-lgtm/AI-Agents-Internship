from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from groq import Groq
from dotenv import load_dotenv
import os 


#rag retrieved argumented generation is teaching the model to answer question using
#my own documents insted of relying on what he already knows 
#its importat bcs LLM cant now privat information (company documents, notes, pdf ), and 
#somtimties they can invent things that dosent even exists do RAG solve these problems

#so for  example if i ulpoad a pdf about basketball and ask a question about it to a LLM :
#the system gonna do the following steps:
#1-reads the document.
#2-converts the text into embeddings (vectors).(embedding are numerical represantation of a text 
    #fo example I=0.23) (so a sentence here is a vector of number where every word= anumber)
#3-stores those vectors in a vector database (ChromaDB or FAISS).
#4-finds the most relevant text chunks related to user question.
#5-sends those chunks to the LLM.
#6-the LLM answers using the retrieved information



#created a description of the titanic dataset as txt document (small one but goodd for rag and to understant it better )
with open("day12/titanic_description.txt","r") as f : #read the document 
    text=f.read()
print ("document loaded")

#let's split the text into small chunks (2 senteces per chunk )
chunks=[s.strip() for s in text.split("\n") if s. strip()]
print(f"created {len(chunks)} chunks ")

#creating an embedding model (converts text into numbers  )
embedding_model=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#create a db where we gonna save the embedded data (transformed)
client_db=chromadb.PersistentClient(path="day12/chroma_db") #that save the db in the disk 
collection=client_db.get_or_create_collection("documents") #its store the data in a relational way (table)

#stor each chunk 
for i,chunks in enumerate(chunks):   #enumerate  loops with index (0, 1, 2...)
    embedding=embedding_model.embed_query(chunks)#for every text chunk convert it to a vector with embed_query
    collection.add(documents=[chunks],embeddings=[embedding],ids=[f"chunks_{i}"])#stor the vector with the original text in chromaDB with a unique ID

question="how many people died on the titanic?"
question_embedding=embedding_model.embed_query(question)#turn the question to a vector too

results=collection.query(query_embeddings=[question_embedding],n_results=2)#chromadb finds two chunks that have vector closest to the question
print("most relevant chunks")
for doc in results["documents"][0]:
    print(f"{doc}")#resturn the first result(most relevant one )



#now lets connect LLM and make him answer the questions that we ask on our document 
load_dotenv(".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

#lets send the rilevent chunks to the LLM because the LLM dosen't see the whole document but only see 
#the rilevant chuank 
context="\n".join(results["documents"][0])
response=client.chat.completions.create(model="llama-3.3-70b-versatile",
    messages=[
    {"role":"system","content":"answer only using the document provided"},
    {"role":"user","content":f"context:\n{context}\n question:\n{question}"}
])
print(" ______LLM answer_________")
print(response.choices[0].message.content)

