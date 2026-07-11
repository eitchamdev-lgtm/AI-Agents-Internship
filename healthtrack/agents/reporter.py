#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul(python 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import json
from healthtrack.utils import call_llm
llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul(pthon -m healthtrack.agents.agent name) because we have the 
# path and tha api and the model in the config file and we imported everything from there

# agent 4: reporter
# job: take everything from all previous agents and produce two things
# 1_ a written health summary report the patient can read and download
# 2_ wo visual graph showing health trends and health score per visit
# it receive 3 inputs:
# timeline from agent 2 (the story)
# conflicts from agent 3 (the problems found)
# extracted_data from agent 1 (the raw numbers)

reporte_prompt=ChatPromptTemplate.from_messages([
("system","""you are a medical report writer 
 write a clear simple health medical report that the patient can understand and maybe 
 show it to thei doctor :
 use this format :
 HEALTH SUMMARY REPORT
     OVERVIEW: [2 sentences about overall health journey]
     KEY FINDINGS: [bullet points of important values and how they changed]
     CONCERNS: [contradictions and gaps found]
     ACTION ITEMS: [simple list of what patient should do next]
     
     no medical jargon write like explaining to an average person """),
     ("human", "timeline:\n{timeline}\n\nconflicts:\n{conflicts}\n\ndata:\n{extracted_data}")])
# we pass  the timeline narrative and the raw extracted data and conflict (gaps) fouunfd in the conflict agent 

#let's connect the reporter prompt to our model
reporte_chain=reporte_prompt|llm

def _systolic(bp):
    # safely extract the first number from a bp string like 145/90 return None if the value is missing junk or 
    # in unexpected format so the plot dont crashe on bad data 
    try:
        return int(str(bp).split("/")[0])
    except (ValueError, AttributeError, IndexError):
        return None
#the old code crashed if the llm returned NA or null insted of a real bp value
#systolic wraps it safley and returns None if the value is junk so we skip it insted of crashing
#if all values are bad show a  mesage insted of a broken chart

def plot_health_trends(extracted_data: list):
    # simple line chart showing blood pressure changing over time
    # we loop through extracted data and pull the date and bp value from each visit
    # bp.split("/")[0] takes only  (first number from 145/90 = 145)
    dates, bp_vals = [], []
    for r in extracted_data:
        bp = r.get("findings", {}).get("blood_pressure", None)
        systolic = _systolic(bp)  # use safe parser instead of direct int()
        if systolic is not None:  # skip rows where parsing failed
            dates.append(r.get("date", ""))
            bp_vals.append(systolic)

    # if no valid bp data show a message instead of crashing
    if not dates:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "no blood pressure data found",
                ha="center", va="center", transform=ax.transAxes)
        return fig

    fig, ax = plt.subplots()
    ax.plot(dates, bp_vals, marker="o", color="#E74C3C", linewidth=2)
    ax.set_title("blood pressure over time")
    ax.grid(True, alpha=0.3)
    # returns the figure so streamlit can display it with st.pyplot(fig)
    return fig




# takes the three inputs from previous agentssends them to the llm to write the report
# generate the graph from the extracted data returns both the report text and the figure
def reporter_agent(timeline: str, conflicts: str, extracted_data: list):
    print("agent 4: writing final health report...")
    extracted_text = json.dumps(extracted_data, indent=2)

    response = call_llm(reporte_chain,
                        {"timeline": timeline,
                         "conflicts": conflicts,
                         "extracted_data": extracted_text}) #with call llm the final report  gets 3 attempts before failing
    

    fig = plot_health_trends(extracted_data)  # generate the graph
    return response.content, fig
    # returns two things:
    # 1_ report text (string) that goes into the streamlit app as text
    # 2_ fig (matplotlib figure) that goes into streamlit with st.pyplot(fig)


# test  (it only run for this file but this block will not run if imported)
#wrote here some example that already got in my sample file mannualy because at this point 
#the agent is not connected to the previous ones 
if __name__ == "__main__":
    test_data = [
        {"clinic": "Chicago Clinic", "date": "2022-03-15",
         "findings": {"blood_pressure": "118/76", "glucose": "95"}},
        {"clinic": "WellMed", "date": "2023-01-10",
         "findings": {"blood_pressure": "145/90", "glucose": "112"}},
        {"clinic": "General Hospital", "date": "2024-06-20",
         "findings": {"blood_pressure": "128/82", "glucose": "108"}}
    ]
    report, fig = reporter_agent("test timeline", "test conflicts", test_data)
    print(report)
    plt.show()      #see our line chart 