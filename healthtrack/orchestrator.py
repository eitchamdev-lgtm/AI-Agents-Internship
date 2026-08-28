#before in the previous orchestrator file we had a problem where the 
#same pdf files are being read 2  or 3 times (once by outrache , and once by extractor)
#this coul not be efficcient and could be slow too because somtimes we have multiple
#medical records and maybe each medical record have 100 page so this could be so slow to do 
#so now what we gonna try to do is to read the pdf once at the begining 
#store what we read from pdf in memory and let all agents if they need info from this pdf 
#instead of readind the pdf the agent can easily go to the text store in memory and read it 
#(faster than reading pdf),and we gonna here is controls the whole pipeline.
#it reads the pdfs once saves the text and passes it to each agent in order.


#import all 5 agents so we can call them in order 
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from healthtrack.agents.outreach import outreach_agent
from healthtrack.agents.extractor import extractor_agent
from healthtrack.agents.timeline import timeline_agent
from healthtrack.agents.conflict import conflict_agent
from healthtrack.agents.reporter import reporter_agent
from healthtrack.agents.investigator import investigator_agent
from healthtrack.agents.critic import critic_agent
from healthtrack.rag import store_reports, ask_question

# import the upload folder path from config so we know where to read files from
from healthtrack.config import UPLOAD_DIR

import os

class HealthState(TypedDict):
    folder_path: str
    raw_texts: dict
    outreach_result: str
    extracted_data: list
    timeline: str
    conflicts: str
    investigation: str
    report: str
    figure: object
    critic_feedback: str
    retry_count: int

#so here what we gonna do is build a function that read file txt and pdf(using pdf plumber) from a folder 
#and return a text in a dict form where the key = file name and value = file or pdf content
#create a counter to make sure odf are read only once

def read_file(folder_path:str)->dict:
    print("reading pdfs from disk-once only")
    #empty dict to store file name and text content 
    raw_texts={}
    #counter =0 to say this gonna be an int and shoudnt be negative 
    read_count=0
    # loop through every file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf") or filename.endswith(".txt"):# only read pdf or txt files
            file_path = os.path.join(folder_path, filename) # build the full file path

            if filename.endswith(".pdf"):#here we gonna use odf plumber because its able to read binary files and extract txts
                import pdfplumber #before i used only open() that work only with txt files but dosent wotk with binary files as pdf so for pdf i shouldve used pdf plumber
                with pdfplumber.open(file_path) as pdf : ## extract text from every page and join with newline and skip empty pages
                    text="\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

            else:
                with open(file_path,"r",encoding="utf-8") as f: #txt file can be opened with itf-8 encoding
                    text=f.read()

            raw_texts[filename]=text #store the text in the dict with file name as a key 

            read_count+=1  #increase the conter on every file read
            print(f"read {read_count}:{filename}")
    
    # print total files read to prove they were read once
    print(f"total files read: {read_count}")
    return raw_texts # return the dict with all file contents

#now gonna build the function that run the pipline 
#that call all agents and passes the datya between them

def node_outreach(state: HealthState) -> HealthState:
    print("\noutreach agent...")
    raw_texts = read_file(state["folder_path"])
    store_reports(raw_texts)
    print("reports stored in chromadb")
    all_text = "\n".join(raw_texts.values())
    result = outreach_agent(all_text)
    print("outreach done")
    return {**state, "raw_texts": raw_texts, "outreach_result": result}


def node_extractor(state: HealthState) -> HealthState:
    print("\nextractor agent...")
    data = extractor_agent(state["raw_texts"])
    print(f"extracted {len(data)} reports")
    return {**state, "extracted_data": data}


def node_timeline(state: HealthState) -> HealthState:
    print("\ntimeline agent...")
    timeline = timeline_agent(state["extracted_data"])
    print("timeline done")
    return {**state, "timeline": timeline}


def node_conflict(state: HealthState) -> HealthState:
    print("\nconflict agent...")
    conflicts = conflict_agent(state["timeline"], state["extracted_data"])
    print("conflict done")
    return {**state, "conflicts": conflicts}


def node_investigator(state: HealthState) -> HealthState:
    print("\ninvestigator agent...")
    investigation = investigator_agent(state["conflicts"])
    print("investigation done")
    return {**state, "investigation": investigation}


def node_reporter(state: HealthState) -> HealthState:
    print("\nreporter agent...")
    combined = state["conflicts"]
    if state.get("investigation"):
        combined += "\n\n" + state["investigation"]

    # explicit revision instruction (not just passive feedback) so the reporter
    # treats this as a required correction on retry, not optional context
    if state.get("critic_feedback"):
        combined += f"\n\nYour previous report was rejected. You MUST address this feedback:\n{state['critic_feedback']}"

    report, fig = reporter_agent(state["timeline"], combined, state["extracted_data"])


def node_critic(state: HealthState) -> HealthState:
    print("\ncritic agent...")
    critique = critic_agent(state["report"])
    if critique["approved"]:
        print("critic: report approved")
        return {**state, "critic_feedback": ""}
    else:
        print("critic: report needs revision")
        return {**state, "critic_feedback": critique["feedback"], "retry_count": state.get("retry_count", 0) + 1}



def route_after_conflict(state: HealthState) -> str:
    # this function decides which agent runs next based on what conflict agent found
    # if conflicts string contains NONE or is empty skip investigator go straight to reporterif real conflicts 
    # found run investigator first for deeper analysis this is the conditional branch the system makes the decision not us
    conflicts_clean = state["conflicts"].strip().upper()
    if "NONE" in conflicts_clean or conflicts_clean == "":
        print("no conflicts found — going straight to reporter")
        return "reporter"
    else:
        print("conflicts found — running investigator first")
        return "investigator"

def route_after_critic(state: HealthState) -> str:
    if not state["critic_feedback"]:
        print("critic approved — pipeline complete")
        return END
    elif state.get("retry_count", 0) <= 1:
        print("critic rejected — rewriting report once")
        return "reporter"
    else:
        print("retry cap reached — ending pipeline")
        return END



workflow = StateGraph(HealthState)

workflow.add_node("outreach", node_outreach)
workflow.add_node("extractor", node_extractor)
workflow.add_node("timeline", node_timeline)
workflow.add_node("conflict", node_conflict)
workflow.add_node("investigator", node_investigator)
workflow.add_node("reporter", node_reporter)
workflow.add_node("critic", node_critic)

workflow.set_entry_point("outreach")
workflow.add_edge("outreach", "extractor")
workflow.add_edge("extractor", "timeline")
workflow.add_edge("timeline", "conflict")

workflow.add_conditional_edges("conflict", route_after_conflict, {
    "investigator": "investigator",
    "reporter": "reporter"
})

workflow.add_edge("investigator", "reporter")
workflow.add_edge("reporter", "critic")

workflow.add_conditional_edges("critic", route_after_critic, {
    "reporter": "reporter",
    END: END
})

app = workflow.compile()


def run_pipeline() -> dict:
    print("_" * 50)
    print("starting healthtrack pipeline")
    print("_" * 50)

    result = app.invoke({
        "folder_path": str(UPLOAD_DIR),
        "raw_texts": {},
        "outreach_result": "",
        "extracted_data": [],
        "timeline": "",
        "conflicts": "",
        "investigation": "",
        "report": "",
        "figure": None,
        "critic_feedback": "",
        "retry_count": 0
    })

    return result

# this block runs only when we execute this file directly
# it runs the pipeline and prints the final report
if __name__ == "__main__":
    results = run_pipeline()
    print("_"*50)
    print("FINAL REPORT:")
    print("_"*50)
    print(results["report"])


#changelog: went back to langgraph after mark review pointed out we removed it in an earlier
#refactor wile claiming "our pipeline is a straight line", but the same commit added a conditional
#branch (investigator) and a critic loop wich are literaly exactly wat langgraph is for so that
#justification didnt realy hold up
#also fixed a bug were extractor_agent was being called twice by acident wasting an extra llm call
#and retry_count now actualy lives in state and gets checked by the graph insted of being just
#a manual if/else that happend to work but had no real loop structure or cap behind it
#no hardcoded paths here either, everything still comes from config.py

