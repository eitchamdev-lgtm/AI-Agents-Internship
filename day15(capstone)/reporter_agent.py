from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os 
import json

load_dotenv(find_dotenv())
llm=ChatGroq(api_key=os.getenv("GROQ_API_KEY"),model="llama-3.3-70b-versatile")

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

def plot_health_trends(extracted_data: list):
    # simple line chart showing blood pressure changing over time
    # we loop through extracted data and pull the date and bp value from each visit
    # bp.split("/")[0] takes only  (first number from 145/90 = 145)
    dates, bp_vals = [], []
    for r in extracted_data:
        bp = r.get("findings", {}).get("blood_pressure", None)
        if bp and bp != "NA":
            dates.append(r.get("date", ""))
            bp_vals.append(int(bp.split("/")[0]))

    fig, ax = plt.subplots()
    ax.plot(dates, bp_vals, marker="o", color="#E74C3C", linewidth=2)
    ax.set_title("blood pressure over time")
    ax.grid(True, alpha=0.3)
    return fig
    # returns the figure so streamlit can display it with st.pyplot(fig)




# takes the three inputs from previous agentssends them to the llm to write the report
# generate the graph from the extracted data returns both the report text and the figure
def reporter_agent(timeline: str, conflicts: str, extracted_data: list):
    print("agent 4: writing final health report...")
    extracted_text = json.dumps(extracted_data, indent=2)

    response = reporte_chain.invoke({
        "timeline": timeline,       # story from agent 2
        "conflicts": conflicts,     # problems found by agent 3
        "extracted_data": extracted_text  # raw numbers from agent 1
    })

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