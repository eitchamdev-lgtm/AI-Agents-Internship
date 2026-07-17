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
User uploads PDFs → Streamlit saves files to data/uploads/

LangGraph starts → Initializes shared state that tracks everything throughout the pipeline

Outreach Agent → Reads all files once (with counter to prove no duplicates), stores chunks in ChromaDB for RAG, identifies providers and missing specialists, calls lookup_provider_contact tool to find emails, generates email drafts

Extractor Agent → Takes raw text from state (never reads disk again), sends each file to LLM, returns structured data (clinic, date, BP, glucose, etc.)

Timeline Agent → Sorts by date using pure Python (reliable), sends sorted data to LLM, builds chronological health narrative

Conflict Agent → Compares timeline and extracted data, finds contradictions (BP changing without medication) and gaps (missing eye exams)

Conditional Branch → If conflicts found, routes to Investigator; if none, skips to Reporter

Investigator Agent (conditional) → Analyzes conflicts deeper, assigns urgency levels, gives specific questions for the doctor

Reporter Agent → Combines all data, writes patient-friendly summary, generates blood pressure graph

Critic Agent → Reviews the report, if not good enough sends it back to Reporter for one rewrite (self-correction loop)

Streamlit displays → Tab 1: email drafts, conflicts, health summary, download button; Tab 2: timeline, blood pressure graph; Tab 3: chat interface with RAG + memory


## data flow
PDFs → Outreach → Extractor → Timeline → Conflict → (Conflicts? → Investigator) → Reporter → Critic → Report
                      ↑                                                                         ↑
                      └───────────── rewrites if needed ──────────────────────────────────────┘

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