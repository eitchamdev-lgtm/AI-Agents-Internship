#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul(python 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
import json
llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)
from healthtrack.utils import call_llm
#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul(pthon -m healthtrack.agents.agent name) because we have the 
# path and tha api and the model in the config file and we imported everything from there


#we need to pull out the sorting data into its own funct so we can test it without touching groq 
def sort_by_date(extracted_data:list)->list: #pure py funct no llm needed , take a list of dict from extractor agent 
                                             #and sort them by date(oldest firsst) , we can test this in pytest without needing an API 
    return sorted(extracted_data,key=lambda x:x.get("date","")) # lambda x: x.get("date", "") means for each dict in the list get the date value from oldest first newest last



# agent 2: timeline builder
# job: take the list of dicts from agent 1 and build a chronological health narrative
# step 1: sort the reports by date in python not LLM because python sorting is 100% reliable
# step 2: pass sorted data to LLM to write a clear human readable narrative

def timeline_agent(extracted_data: list) -> str: 
    sorted_data =sort_by_date(extracted_data)
    print("agent : building health timeline...")
    # convert sorted list to a string so we can pass it to the llm
    sorted_text = json.dumps(sorted_data, indent=2) #json.dumps turn the dorted list to a string (with good space)


    # pass to llm to write a human readable narrative
    prompt = ChatPromptTemplate.from_messages([
        ("system", """you are a medical historian
         take the structured medical data sorted by date and write a clear chronological health narrative
         for each visit include date clinic doctor findings diagnosis and notes
         keep it simple and clear and use this format:
         
         HEALTH TIMELINE
         [DATE] — [CLINIC] — [DOCTOR]
         findings: [key values]
         diagnosis: [diagnosis]
         notes: [notes]"""),
        ("human", "{sorted_data}")
    ])

    #connect prompt to llm 
    chain = prompt | llm
    response = call_llm(chain, {"sorted_data": sorted_text})#runs it
    #The timeline agent make one  llm call with all the sorted data  if that single call fail
    # the whole timeline is lost and everything after it (conflict agent, reporter) cant run either.
    #with call_llm that one important call gets 3 attempts
    return response.content
    # returns a clean readable timeline string that gets passed to the next agent 


# test         (it only run for this file but this block will not run if imported)
#here i will write the list of dicts mannualy becaus at this point this agent its not connected to the previous one 
if __name__ == "__main__":
    print("=== TESTING TIMELINE AGENT ===")
    
    test_data = [
        {"clinic": "WellMed", "date": "2023-01-10", "doctor": "Dr. Jones",
         "findings": {"blood_pressure": "145/90"}, "diagnosis": "Pre-hypertension"},
        {"clinic": "Chicago Clinic", "date": "2022-03-15", "doctor": "Dr. Smith",
         "findings": {"blood_pressure": "118/76"}, "diagnosis": "Healthy"}
    ]
    
    print("Test data:", test_data)
    result = timeline_agent(test_data)
    print("\n RESULT \n")
    print(result)

#so this agent takes the list of dict that we got in extractor agent the sort it then convert it 
#to a string then pass it to the llm and the llm 
#returns a clean readable timeline string that gets passed to the next agent 

