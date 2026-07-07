# healthtrack-mas
a multi agent system that analizes medical records from multiple clinics and hospitals and generates a patient friendly health summary

## what it does
upload your medical pdfs or txt reports and the system will:
- identify missing providers and generate email drafts to request records
- extract structured health data from every report like blood presure and glucose
- build a chronological health timeline across all your visits
- detect contradictions and gaps across all reports
- run a deeper investigation if conflicts are found
- write a patient friendly summary with a blood presure graph
- self correct the report using a critic agent if the first draft isnt good enough

## architecture
outreach → extractor → timeline → conflict → investigator (only if conflicts) → reporter → critic → rewrite if needed
- agent 0 outreach: finds missing providers and writes email drafts using a real tool lookup
- agent 1 extractor: pulls structured medical facts from each report
- agent 2 timeline: sorts everything by date into a health story
- agent 3 conflict: finds contradictions like bp changing without medication
- investigator: only runs if conflicts found digs deeper and assigns urgency levels
- agent 4 reporter: writes the summary and creates a blood presure graph
- critic: reviews the report and sends it back for rewriting if its not good enough
- all agents share data through the orchestrator pdfs are read once and passed through memory

## setup
1. clone the repo
```bash
git clone https://github.com/eitchamdev-lgtm/AI-Agents-Internship.git
cd AI-Agents-Internship
```
2. install dependecies
```bash
pip install -r healthtrack/requirements.txt
```
3. copy env.example to .env and add your groq api key
GROQ_API_KEY=your_key_here
4. run the app
```bash
python -m streamlit run healthtrack/app.py
```

## sample data
the files in data/sample_reports are synthetic and invented for testing only
replace them with your real medical reports to use the system

## tech stack
- groq api llama-3.3-70b-versatile as the llm
- langchain for agent chains and prompts
- chromadb for persistant vector storage
- huggingface embeddings for rag
- pdfplumber for pdf reading
- streamlit for the web interface
- pytest for testing