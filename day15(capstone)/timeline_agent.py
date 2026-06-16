from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os
import json

load_dotenv(find_dotenv())
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

# agent 2: timeline builder
# job: take the list of dicts from agent 1 and build a chronological health narrative
# step 1: sort the reports by date in python not LLM because python sorting is 100% reliable
# step 2: pass sorted data to LLM to write a clear human readable narrative

def timeline_agent(extracted_data: list) -> str: #extracted_data is the list from agent extractor (one dictionary per medical report)
    # sort by date oldest to newest
    # lambda x: x.get("date", "") means for each dict in the list get the date value from oldest first newest last
    sorted_data = sorted(extracted_data, key=lambda x: x.get("date", ""))
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
    response = chain.invoke({"sorted_data": sorted_text})#runs it
    return response.content
    # returns a clean readable timeline string that gets passed to the next agent 


# test         (it only run for this file but this block will not run if imported)
if __name__ == "__main__":
    test_data = [      #here i will write the list of dicts mannualy becaus at this point this agent its not connected to the previous one 
        {"clinic": "WellMed", "date": "2023-01-10", "doctor": "Dr. Jones",
         "findings": {"blood_pressure": "145/90"}, "diagnosis": "Pre-hypertension"},
        {"clinic": "Chicago Clinic", "date": "2022-03-15", "doctor": "Dr. Smith",
         "findings": {"blood_pressure": "118/76"}, "diagnosis": "Healthy"}
    ]
    result = timeline_agent(test_data)
    print(result)

#so this agent takes the list of dict that we got in extractor agent the sort it then convert it 
#to a string then pass it to the llm and the llm 
#returns a clean readable timeline string that gets passed to the next agent 
