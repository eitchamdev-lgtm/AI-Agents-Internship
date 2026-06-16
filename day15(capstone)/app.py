
import streamlit as st
import matplotlib
matplotlib.use("Agg")  # fix for streamlit so matplotlib dosent open a separate window
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # so streamlit can find the files

from orchestrator import run_pipeline  # the function that runs all 5 agents in order
from rag import ask_question           # the function that answers questions from chromadb

# the folder where  gonna save the uploaded files so our agents can read them
UPLOAD_FOLDER = r"C:/Users/Lenovo/AI-Agents-Internship/day15(capstone)/sample_reports(to"

st.set_page_config(page_title="HealthTrack-MAS", page_icon="🏥")
st.title("🏥 HealthTrack-MAS")
st.markdown("upload your medical reports and ill analyze your full health history")

# file uploader that accept multiple pdf or txt files at the same time
uploaded_files = st.file_uploader("upload your reports", type=["pdf","txt"], accept_multiple_files=True)

if st.button(" analyze") and uploaded_files:
    # save each uploaded file to the sample reports folder so agents can access them
    for file in uploaded_files:
        with open(os.path.join(UPLOAD_FOLDER, file.name), "wb") as f:
            f.write(file.read())

    # run all 5 agents in order using langgraph and save the result in session state
    # session state is used here so the result dont dissapear when streamlit reruns
    with st.spinner("agents analyzing your records..."):
        st.session_state.result = run_pipeline(UPLOAD_FOLDER)
        st.session_state.done = True

# only show results if the analysis is done
if st.session_state.get("done"):
    result = st.session_state.result

    # 3 tabs: one for the report one for the graph and one for the chat
    tab1, tab2, tab3 = st.tabs(["📋 report", "📊 graph", "💬 chat"])

    with tab1:
        # show the email drafts in a collapsible section
        with st.expander("📧 email drafts for missing records"):
            st.write(result["outreach_result"])
        st.subheader("conflicts and gaps")
        st.write(result["conflicts"])        # contradictions and gaps found by agent 3
        st.subheader("health summary")
        st.write(result["final_report"])     # patient friendly report from agent 4
        st.download_button("⬇ download report", result["final_report"], "health_report.txt")

    with tab2:
        st.subheader("health timeline")
        st.write(result["timeline"])         # chronological narrative from agent 2
        if result["figure"]:
            st.pyplot(result["figure"])      # blood pressure graph from agent 4

    with tab3:
        # chat interface using rag so user can ask questions about all their reports
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # redraw all previous messages so they dont dissapear on rerun
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("ask anything about your reports...")
        if question:
            st.session_state.messages.append({"role":"user","content":question})
            answer = ask_question(question)   # rag find relevant chunks and llm answers
            st.session_state.messages.append({"role":"assistant","content":answer})
            st.rerun()  # rerun so the new messages show up immediately
