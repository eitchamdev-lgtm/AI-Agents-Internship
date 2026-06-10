from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv,find_dotenv
import os 

load_dotenv(find_dotenv()) #find_dotenv() automatically searche parent folders to find the .env file no matter whereirun the script from
llm=ChatGroq(api_key=os.getenv("GROQ_API_KEY"),model="llama-3.3-70b-versatile")

#-----------------------------------------------------------------------------------------------------------
#first after trying to understand what is multiagent and how does it works:
#untill now i had one LLM doing everything now in this concept we gonna 
#have in our example two agents that do two diffrent jobs 
#agent 1:researcher ,job :takes a topic  finds key facts, points, structure
#agent 2: writer , job : takes the resercher output and write a full article out of it for example
#one feed the other the output of agent 1 becomes the input of agent 2 

#and this is a better approach because: because when we have one agent that gonna do both 
#searching and writing , ye she can do it but he does it poorly 
#instead when we have two agents one only writes and another only reserche 
#we gonna have much better results becaus each agent have a focused job and a good prompt for that job 

#so the idea of multiagent : it's not about having multiple models it's about having multiple prompts that give the same 
# model completely different roles and instructions.
#---------------------------------------------------------------------------------------------------------------------

#agent1: researcher prompt:
researcher_prompt=ChatPromptTemplate.from_messages([
    ("system",""" you are an expert researcher.
     your job is to research a topic and produce a well structured notes that  include:
     -main concept explained simply 
     -5 key facts
     -important statistic or number if rilevant 
     -current trend 
     -potential future developpment
     keep it factual structured and detailed"""),
     ("human","{topic}")])

#let's connect the researcher prompt with our model
researcher_chain=researcher_prompt|llm

#let's build a simple researcher function that we can call with the topic and that return 
#the model (agent) the notes 

def researcher_agent(topic:str)->str:
    print(f"researcher working on {topic}")
    response=researcher_chain.invoke({"topic":topic})
    return response.content


#agent2: writer prompt 
writer_prompt=ChatPromptTemplate.from_messages([
    ("system",""" you are an expert writer 
     your job is to take the reearcher prompt then transforme it into well wetitten article 
     the atricle should include:
     -an engaging introduction 
     -clear and well structured sections with headers 
     -smooth natural writhing (no bullet points)
     -a strong conclusion
     keep it informative , engaging and easy to read"""),
     ("human", "write an article based on these research notes:\n{research_notes}")])

#let's connect the writer prompt to our model 
writer_chain=writer_prompt|llm

#let's build a simple writer function that have as in input the notes we got by the resercher 
#agent and returns a well structured written article 
def writer_agent(research_notes:str)->str:
    print("writer working on the article ")
    response=writer_chain.invoke({"research_notes":research_notes})
    return response.content


#let's connect both agents (researcher then writer )
# ----------------ORCHESTRATOR--------------------
def content_creator(topic: str) -> dict:
    print(f"\n starting content creation for: {topic}\n")
    
    # step 1: researcher agent runs first
    research_notes = researcher_agent(topic)
    print("\n research done\n")
    
    # step 2: writer agent takes researcher output
    article = writer_agent(research_notes)
    print("\n article done\n")
    
    return {
        "topic": topic,
        "research_notes": research_notes,
        "article": article
    }

#let's test it
if __name__ == "__main__":
    result = content_creator("artificial intelligence in healthcare")
    print("\n RESEARCH NOTES:")
    print(result["research_notes"])
    print("\n FINAL ARTICLE:")
    print(result["article"])


