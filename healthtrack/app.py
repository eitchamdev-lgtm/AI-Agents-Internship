import os
import streamlit as st
import matplotlib
matplotlib.use("Agg")  # fix so matplotlib doesn't open a separate window

from healthtrack.config import UPLOAD_DIR ## import the upload folder path from config

from healthtrack.orchestrator import run_pipeline # import the pipeline function that runs all agents in order
from pathlib import Path
from healthtrack.rag import ask_question

# set up the page
st.set_page_config(page_title="HealthTrack", layout="wide")
st.title("🏥 HealthTrack — Medical Report Analyzer")
st.markdown("""upload your medical reports and I will analyze your full health history
all files are read once and processed by five specialized agents""")


# create the upload folder if it doesn't exist
# this uses the path from config which is already built with pathlib 
os.makedirs(UPLOAD_DIR, exist_ok=True)

# file uploader
uploaded_files = st.file_uploader("upload your reports",
    type=None,
    accept_multiple_files=True)

if st.button("🔍 analyze my reports") :
    if not uploaded_files: #more robust app is someone didnt upload any file send a warning
        st.warning("please upload at least one report first")
        st.stop()
    # save each uploaded file to the upload folder
    for file in uploaded_files:
        # save each uploaded file to the upload folder
        # the path comes from config and works on any machine
        file_path = UPLOAD_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    
    st.success(f" uploaded {len(uploaded_files)} files")
    # check folder is not empty before running pipeline
    # if somehow no files made it to the folder show an error not a crash
    if not any(Path(str(UPLOAD_DIR)).iterdir()):
        st.error("please upload at least one medical report first")
        st.stop()

    # run the pipeline
    with st.spinner("agents are analyzing your records..."):
        results = run_pipeline()
        st.session_state.results = results
        st.session_state.done = True

# show results if analysis is done
if st.session_state.get("done"):
    results = st.session_state.results
    
    tab1, tab2, tab3 = st.tabs(["📋 report", "📊 graph", "💬 chat"])
    
    with tab1:
        st.subheader("📋 health summary")
        st.write(results["report"])
        
        st.download_button( " download report",
            results["report"],
            "health_report.txt")
    
    with tab2:
        st.subheader("📊 health timeline")
        st.write(results["timeline"])
        
        if results.get("figure"):
            st.pyplot(results["figure"])
    
    with tab3:
     st.subheader("💬 ask anything about your medical records")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # redraw chat history so messages dont disappear on rerun
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("ask anything about your reports...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("searching your records..."):
                answer = ask_question(question)
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

#full logic and flow:
#1_ upload a file by clicking the upload buttonthe file might already be on  disk in a folder like downloads or desktop

#2_when you upload it the app reads it from that folder into memory(RAM, to proccess it)the file is now in memory 
#         but it is not in the upload folder yet

#3_the app takes the file from memory and saves a copy to the upload folder on your diskthe upload folder path comes 
#        from config py and is built with pathlib

#4_the path points to AI Agents Internship healthtrack data uploadswe save it again because 
#          the pipeline only reads from this specific folder
#         if we did not copy it to the upload folder the pipeline would not know where to find it

#now the file is in the right folder and the pipeline can see it

#5_click the analyze button
#6_the pipeline starts running
#7_the pipeline looks at the upload folder and reads every file in itit reads each file once and stores the text in memory
#8_ counter prints how many files were read so we can prove each file was read only once

#9_the pipeline sends the raw text to the outreach agent which finds missing providers and writs email drafts
#10_then the raw text goes to the extractor agent which pulls out key medical facts like blood pressure glucose and dates
#11_the structured data goes to the timline agent which sorts everything by date and builds a health story
#12_the timline and extracted data go to the conflict agent which finds contradictions 
#13_everything goes to the reporter agent which wirtes a patient friendly summary and creates a blood pressure grapgh
#the results show up in the streamlit app as a report graph and timline and you can download the report as a text file
#the whole pipeline uses the same upload folder for saving and reading so everything connects propperly

# note: i was thinking to find a solution that allow us  to avoid doing a copy of the user uploaded pdf(medical report) in the folder uploads
# because my  app saves a copy of the uploaded file to the uploads folder on the user machine i noticed that this is 
# different from LLM like chatgpt  which save files to their cloud servers(and they read from memory) so here in my case i think i have to
#  save locally because  agents read from disk and the pipeline runs entirely on the user machine
#and its common that reading from memory is faster than reading from disck(memory paramyde), i think in our case reading from memory is 
#much difficult because we had to pass files content to each agent mannyaly (i thinks) so rading from disck is simpler since we create 
#folder path and this folder path is where we want our files copy to be so any agent want content can go direactly to that folder(uploads)(local folder)


#sys.path.insert forces Py to find modules	Py finds modules naturally 