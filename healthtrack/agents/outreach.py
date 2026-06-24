#now we rewrite the imports after setting up correctly the cong.py 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model

#agent 0: outreach_agent
# runs before all other agents
# two scenarios it handle:
# scenario A: user uploads PDFs we extract text and pass it here
# scenario B : user just types their medical history in text
# in both cases the agent does the same 3 things:
# 1_ identify all providers mentioned
# 2_ infer what providers are "probably" missing based on medical logic
# 3_ write email drafts  request those missing records

outreach_prompt=ChatPromptTemplate.from_messages([
("system", """ you are a medical record assistant ,
 your job is to help patients to collect all their medical records.
given either uploaded PDF text OR a described medical history:
 
 -identify all clinics hospitals and doctors visited 
 -infer any missing providers the patient should have seen (example: high blood pressure then should have seen a cardiologist)
 -find their medical records request email address (use common patterns like records@[clinicname].com or medicalrecords@[hospital].org)
 (or try to get the email visiting clinic, hospital , doctor website)
 -write a professional email  requesting medical records for the patient
 -note:Generate ONE email per provider

format your response exactly like this:
 
PROVIDERS VISITED:
- [provider name]

MISSING PROVIDERS:
- [provider name] - [reason why needed]

EMAIL DRAFTS:
To: [provider name]
Subject: Request for medical records
[email body]

--- next email ---
To: [next provider]"""),
("human", "{user_input}")]) # {user_input} is the blank that gets filled with whatever the user provide(pdfs or text)

#connect prompt to model 
outreach_chain=outreach_prompt|llm


#outreach agent function 
def outreach_agent(user_input:str)->str:                    #takes one input user input (and it can be pdf or text description)
    print("Analysing your medical history...")
    response=outreach_chain.invoke({"user_input":user_input})  #pass it to the chain which fills {user_input} and send it to LLM 
    return response.content                                     #return the response as a string 


# Test                                (it only run for this file but this block will not run if imported)
if __name__ == "__main__":
    # Test with medical history
    result = outreach_agent("Patient has diabetes and high blood pressure visited Chicago Clinic in 2022.")
    print(result)

#cannot run it directly from python as a script we should run it as a modul because we have the path and tha api and the model in the config file and we imported everything from there 