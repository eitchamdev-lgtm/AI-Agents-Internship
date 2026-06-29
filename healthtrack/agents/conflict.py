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
from healthtrack.utils import call_llm

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul(pthon -m healthtrack.agents.agent name) because we have the 
# path and tha api and the model in the config file and we imported everything from there

#conflict detector  agent:
#takes the timline from the timline agent and take the data from the extractor agent and do 2 things:
#1_contradictions: same value measured differently at two clinics 
#2_gaps: things that couldve been checked but no records exists 
#i decided to do an agent for these things because on llm doing everything weoul miss in these 
#details so this agrent has one job be detective nad finds problems 

conflict_prompt=ChatPromptTemplate.from_messages([
    ("system",""" tou are an expert medical fact checker and detective :
     you job is to analyse patient helath timline and exctract eports and find two things:
    1_contradictions: when same helath value change tottaly beween two visits wthout an explanation 
     example: bp 145/90 in jan 2023 then 128/82 in june 2024 with no medication prescribed
    2_import health check that are missing 
       example: no blood work done in over a year
    use exactly this format:
    [contradictions found]  :-tell the patient the two contradictions founded and the name of the clinics/hospitals involved 
    [gaps that are missing] :-describe what is missing and why it matters 
    [recommandation]: what the patient should ask thei doctor about
     -if nothing found right NONE for the relative section"""),
    ("human","timeline:\n{timeline}\n\nextracted data:\n{extracted_data}")])
# we pass both the timeline narrative and the raw extracted data
# timeline gives the story extracted data gives the exact numbers to compare

#let's connect the conflict prompt to our model 
conflict_chain=conflict_prompt|llm


# conflict agent function takes two inputs:
# 1_ timeline: the narrative string that agent(timeline agent)  returned
# 2_ extracted_data: the list of dicts that agent(extractor agent) returned
# it passes both to the llm so the llm can compare numbers across reports
# and find contradictions and gaps
# returns a string with all the problems found
def conflict_agent(timeline:str,extracted_data:list)->str:
    print("conflict agent detecting contradictions and gaps...")
    # convert the list of dicts to a string because llm only accepts text
    extracted_text = json.dumps(extracted_data, indent=2)
    
    # pass both the timeline and the raw numbers to the llm
    response = call_llm(conflict_chain, 
                        {"timeline": timeline,
                        "extracted_data": extracted_text})
    #if this llm call fail with no retry the patient never sees the conflicts found which fails the whole purpos of the system
    #with call_llm this critical call gets 3 attempt before giving up
    return response.content


# test (it only run for this file but this block will not run if imported)
#wrote here some example that already got in my sample file mannualy because at 
#this point the conflict agent is not connect to the previous two agents 
#and in oeder for this agent to run and see its results we need both timline and extractor agents output
if __name__ == "__main__":
    test_timeline = """         
    2022: chicago clinic bp 118/76 glucose 95 healthy
    2023: wellmed bp 145/90 glucose 112 pre-hypertension no medication
    2024: general hospital bp 128/82 glucose 108 eye exam overdue
    """

    test_data = [
        {"clinic": "WellMed", "date": "2023-01-10",
         "findings": {"blood_pressure": "145/90"}, "notes": "no referral made"},
        {"clinic": "General Hospital", "date": "2024-06-20",
         "findings": {"blood_pressure": "128/82"}, "notes": "eye exam overdue"}
    ]

    result = conflict_agent(test_timeline, test_data)
    print(result)