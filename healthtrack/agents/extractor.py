#now we rewrite the imports after setting up correctly the cong.py 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
from healthtrack.utils import call_llm

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul because we have the 
# path and tha api and the model in the config file and we imported everything from there

#agent 1 extractor agent: job: reay every pdf and extract structured health data from each one 
#taked folder path where all pdf are stored then reads pdf with pdf plumber then passes each text 
#to LLM that will excract important medical facts and return a list of dict (one dict per report)
#so next the agent is able to work with strutured data 
#why we must use structured data here? because timline agent need to sort by date 
#and conflict agent need to compare values across reports 

extractor_prompt=ChatPromptTemplate.from_messages([
("system", """ you are an expert data exctractor 
 extract key information from this medical report and return only JSON object,
 ps: no extra text or explanation just the  JSON:
 JSON format:
     {{"clinic": "clinic name",
        "date": "YYYY-MM-DD",
        "doctor": "doctor name",
        "findings":
      {{"blood_pressure": "value or NA",
        "glucose": "value or NA",
        "cholesterol": "value or NA",
        "weight": "value or NA"}},
        "diagnosis": "main diagnosis",
        "medications": "medications or none",
        "notes": "any important notes"}}
 if a value is not mentioned write NA"""),
 ("human","{report_text}")]) #report text get filled with the raw text exctraced from the pdf 

#connect the excractor prompt with the llm 
extractor_chain=extractor_prompt|llm

#exctractor agent function that take the dictionary of raw texts (key=file name,value=file text content)
#  as an input and return a list of dict where we gonna get one dict of report
#not lets build the exctractor agent function that take raw text from memory (already read by orchestrator)
#it loops through each file (value of dict , because it tales a dict as input), send text to llm
#the ll return structured json we parse the j json and add it to a list ,and we return 
#the list of structured data 
def extractor_agent(raw_texts:dict)->list:
    extracted_data=[]
    for filename,text in raw_texts.items():#loop each file(key)and it text content of  the dict raw_texts read by the orchestrator
        print(f"agent is extracting data from {filename}")

        response = call_llm(extractor_chain, {"report_text": text})#take the content of each file(take the value of each key)
                                                              #invoke the chainn that have the prompt 
                                                              #that tel the llm what to to and how we want the output to be 
                                                              #send the prompt and the file text content to the llm to get the json output 

        clean=response.content.strip()#clean the response and remove spaces and md formatting
        clean = clean.replace("```json", "").replace("```", "").strip()

        #convert the json string to a python dict 
        try:
            data=json.loads(clean)
            data["source_file"]=filename #add the file name so we know which report it came from 
            extracted_data.append(data)
        except  json.JSONDecodeError:#in case json pasing fails save the raw text so we dont loose it 
            extracted_data.append({"source_file":filename,"raw_text":text})
    return extracted_data


# this block runs only when we execute this file directly
# it is used for testing the agent alone
if __name__ == "__main__":
    from healthtrack.config import SAMPLE_DIR # import the sample folder path from config
    from healthtrack.orchestrator import read_file # import the read_file function from orchestrator to read files once
    raw_texts = read_file(str(SAMPLE_DIR)) # read the sample files once
    results = extractor_agent(raw_texts)

    for r in results:
        print(r)


# what we updated in extractor py compared to the old script old code used to read files from disk inside the agent
# old code had a function called readpdfs that read files every time this meant the same files were read multiple times

# new code does not read files from disk at all new code takes raw text from memory passed by orchestrator
# the orchestrator already read the files once at the start

#this is better because:
# no duplicate reads means faster execution,no hardcoded paths inside the agent
# the counter in orchestrator proves files are read exactly once
# the agent is now pure data transformation not file io


#changed : response = extractor_chain.invoke({"report_text": text}) to
# response = call_llm(extractor_chain, {"report_text": text})

#The extractor agent call the llm once per report so if you have 5 reports it makes 5 LLM calls if any one of those calls fails the whole extraction crashes and lose all the data
#with call_llm each of those 5 calls gets 3 attempts before giving up  more reliable when processing multiple files.