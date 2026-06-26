# HealthTrack-MAS
a multi agent system that analizes medical records from multiple clinics and hospitals

## What it does
_ upload your medical pdfs or text reports and 5 specialized agents will work on them
_ identify missing providers and generate email drafts to request records
_ extract structured health data from every report like blood pressure and glucose
_ build a chronological health timeline from all your visits
_ detect contradictions and gaps across all reports
_ write a patient friendly summary report with a blood pressure graph

## Architecture
_ agent 0 outreach finds missing providers and writes emails
_ agent 1 extractor pulls out medical facts from each report
_ agent 2 timeline sorts everything by date into a health story
_ agent 3 conflict finds contradictions like bp changing without medication
_ agent 4 reporter writes a patient summary and creates a graph
_ all agents share data through the orchestrator
_ pdfs are read once and passed through memory

## Setup
1 clone the repo
2 create a virtual environment and install dependencies
pip install -r requirements.txt
3 copy env example to env and add your groq api key
GROQ_API_KEY=your_key_here
4 run the app
python -m streamlit run healthtrack/app.py

## Sample data
the files in data sample reports are synthetic and invented for testing only
replace them with your real medical reports to use the system