from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
import os
from langchain_core.tools import tool # so we cann tools @tool and tell the LLM that he can use this tool 
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


#here i decided to make a reserche helper that respond the user on the reserche question :
#so first i built the model and the prompt and connected them with a chain the did a dictionary to 
#store in memory specifidef in conversation how the chat history will be saved in memory and how the workflow works

#then i built some tool that the model gonna ask the user after the first response if he want to use 
#one of those 3 tools that im gonna bild in this file and im gonna wrap everything in a st interface 
#in anotherfile that im gonna call ResearchHelper_app.py




#load the file where i got the api key 


#save the model into the variable llm 
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

#--------------------------tools-----------------------------------------------------------
@tool
def summarize(topic:str) ->str:
    """ summurize the topic giving as the output the key points(concepts), and important facts """
    response=llm.invoke(f"""   give a structure summary of {topic} and include:
                        -what the topic is about in 2 lines
                        -3 key points
                        -1fun fact""")
    return response.content

@tool
def compare(topics:str)->str:
    """ comapre 2 topics side by side using this format topic1,topic2"""
    response=llm.invoke(f"""   compare two topic side by side {topics} and include:
                        -what do they have in common
                        -what diffrences they have 
                        -when to use each topic/concept """)
    return response.content

@tool
def quiz(topic:str)->str:
    """ generate 5 question quinz with answers to test knowledge aboy topic"""
    response=llm.invoke(f"""   generate a 5 question quiz about {topic} and include for each question:
                        -write the question 
                        -give 4 multiple answer choices (a,b,c,d)
                        -reveal the correct answer""")
    return response.content

#bind the tools to the llm so the LLM knows they exist and the LLM gonna be able to use them
tools=[summarize,compare,quiz]
llm_with_tools=llm.bind_tools(tools)


#--------------------------------------------------------------------------------------------------

#create a prompt with memory chat history 
prompt = ChatPromptTemplate.from_messages([
    ("system", """you are an expert research assistant. 
     when given a topic give a clear structured summary with key points.
     when asked follow up questions use the conversation history to give accurate answers"""),
    ("placeholder", "{chat_history}"),   #is where the previous messages get inserted automatically
    ("human", "{input}") ])           #user input

#connect the preompt to the model 
chain = prompt | llm_with_tools

#dict to store conversation history in memory
store = {}


def get_session_history(session_id: str):            #check if session exists and if not it creates one 
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory() 
    return store[session_id]

#RunnableWithMessageHistory :   take the chain,
# then load previous convo from store(using get_session_history),
#inject it into {chat_history} in the promp (using history_messages_key=)
# save the new message after the response (using input_messages_key)
conversation = RunnableWithMessageHistory(chain, get_session_history,
                                          input_messages_key="input",
                                          history_messages_key="chat_history")

#store is the physical place where history lives (a dictionary in RAM)
#chat_history is the window the LLM looks through to see that history

#so how i run  RunnableWithMessageHistory and how it works when i run it 
#to runt it we use conversation.invoke() 
#1_ RunnableWithMessageHistory opens store["session4"]   (for example)
#2_ takes everything inside it
#3_ puts it into {chat_history} in the prompt
#4_ LLM reads the prompt (which now contains the history)
#5_ LLM responds
#6_ new message gets added back into store["session4"]




