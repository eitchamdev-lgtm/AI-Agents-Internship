from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os 
from langchain_core.chat_history import InMemoryChatMessageHistory   #to save chat in memory instead of saving it mannualy in a list 
from langchain_core.runnables.history import RunnableWithMessageHistory

#chatgroq:instead of doing client.chat.complections.create() langchain handle it directly 
#in the background when i use chatgroq

#chatprompt template: let me build reusable prompt templates with variables

#the goal here instead of doing everything mannualy like build a message array myself 
#sent it to groq then read groq response now instead of doing this mannualy every time
#from scratch with langchain we gonna snap together pre_built peaces (prompt template, llm)
#and connect them together with a chain and make llm remember the conversation (memory)


load_dotenv(".env")

#the model now is the variable llm 
llm=ChatGroq(api_key=os.getenv("GROQ_API_KEY"),model="llama-3.3-70b-versatile")

#lets create a prompt template 
prompt=ChatPromptTemplate.from_messages([                      #reusable template 
    ("system","you are a helpful assistant that explains topic clearly "),
    ("human","{topic}")])    #topic is the black to fill each time 

#connect the model with the prompt 
chain=prompt|llm          #  |: mean send prompt to llm 

#run everything using the chain and apssing into it the variable 
response=chain.invoke({"topic":"explain what is machine learning in 3 lines "})
print(response.content)

#before i used to do client.chat.completions.create(model=..., messages=[...]) now 
#just calling the model with chatgroq and saving the prompt template with a variable 
#and connecting them with a chian i can just do chain.invoke({"topic": "anything i want"})


#---------------------------add memory (prompt with chat history memory )-------------------------
prompt_with_memory=ChatPromptTemplate.from_messages([
    ("system","your are a efficient and helpful reseache assistant"),
    ("placeholder","{chat_history}"), #is where the previous messages get inserted automatically
    ("human","{input}")])

#connect the model to the promt with memory
chain_with_memory=prompt_with_memory|llm

store={} #dictionary to save conversation history in memory 

def get_session_history(session_id:str):   #check if session exists and if not it creates one 
    if session_id not in store:            #session_id is like conversation id 
        store[session_id]=InMemoryChatMessageHistory()    #wrap the chian and automatically inject the chat history into every message
    return store[session_id]   

#chain_with_memory at this point dosent know about saving or loading history 
#it just take an input and give back a response an output 

#RunnableWithMessageHistory upgrades (chain_with_memory) by doing 3 things automatically before every message:
#load the previous conversation from store
#Injects it into {chat_history} in the  prompt
#saves the new message after the response

conversation=RunnableWithMessageHistory(chain_with_memory,get_session_history,
                                        input_messages_key="input",
                                        history_messages_key="chat_history")

response1=conversation.invoke({"input":"my name is Elias"},
                              config={"configurable":{"session_id":"session1"}})
print(response1.content)

response2=conversation.invoke({"input":"what is my name?"},
                              config={"configurable":{"session_id":"session1"}})
print(response2.content)

#here just thinking how it actually working at the back end and the logic on how its running and i came up with this:

#for respons1 one :
#1_ conversation.invoke is called:(where in it i have the chian with memory where model and prompt are connected),
#and in it we have the get_session_history that return session_id if history exists and if session dosent exists
#create a new session with her own id
#2_ RunnableWithMessageHistory cheks store["session1"]
#3_store is empty so it gonna creat a new empty history 
#4_injects the empty history into {chat_history}
#5_send to LLM, LLM respond 
#6_save the input +response into store["session1"]


#for response2 two:
#1_ conversation.invoke is called again:(where in it i have the chian with memory where model and prompt are connected),
#and in it we have the get_session_history that return session_id if history exists and if session dosent exists
#2_  RunnableWithMessageHistory cheks store["session1"]
#3_ find response1 saved there in store["session1"]
#4_ put it into {chat_history}
#5_ LLM now sees BOTH messages + answers 
#6_ save this new message into store["session1"] too
