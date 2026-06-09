import os 
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

#i decided to to an intreactive bot that allow the user to upload a text document 
#and ask any question about it and im gonna do the RAg and convert text to vectors(numbers)
#and pass it to the LLM and let himn send the answer on the question 

load_dotenv(".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY")) #connect groq
embedding_model=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") #connect the embedding model 

st.title("Document QA")
st.markdown("upload a text file and ask anything about it ")
uploaded_file=st.file_uploader("upload your document",type=["txt"])#allow the user to uplaod the file but retutn it as byte not text 

#now we wanna read the file and divide it in chunks 
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    #read the file and decode it from bytes to text so we can work with it in python 
    chunks=[s.strip() for s in text.split("\n") if s.strip()]
    st.success(f"document loaded :{len(chunks)} created ")

    #store chunks in chromadb
    client_db = chromadb.Client() 
    collection = client_db.get_or_create_collection("documents")
    for i, chunk in enumerate(chunks):
        embedding = embedding_model.embed_query(chunk)  #covets it to a vector usding huggingface
        collection.add(documents=[chunk], embeddings=[embedding], ids=[f"chunk_{i}"])#then stores the vector + original text in Chromasdb after this loop the entire document is stored as vectors in memory.

    #question input
    question=st.text_input("ask a question about the document you just uploaded ")
    if st.button("ask"):
        if question !="":
            # only run if the user click on ask bottom and the input question box is not empty
            #passing to LLM rilevant chunk 
            question_embedding = embedding_model.embed_query(question)
            results = collection.query(query_embeddings=[question_embedding], n_results=2)
            context = "\n".join(results["documents"][0])
            #find the most two rilevant chunks and joins them in one string in the variable context 

            #send the rilevant to chunks and make him send the first (most rilevant) chunks as an answer 
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "answer the question using only the context provided. if the answer is not in the context say i dont know"},
                    {"role": "user", "content": f"context:\n{context}\n\nquestion: {question}"}
                ]
            )
            st.success("answer:")
            st.write(response.choices[0].message.content)



