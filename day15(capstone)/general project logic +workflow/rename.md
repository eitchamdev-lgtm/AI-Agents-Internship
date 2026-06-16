# HealthTrack-MAS

A multi-agent AI system that analyzes your full medical history.

## What it does
- reads your medical PDFs and txt reports
- extracts structured health data from each report
- builds a chronological health timeline
- detects contradictions and gaps across reports
- writes a patient friendly summary report
- generates a blood pressure graph
- lets you ask questions across all your reports using RAG

## How to run
1. install dependencies: pip install -r requirements.txt
2. add your GROQ_API_KEY to a .env file
3. run: streamlit run app.py

## Architecture (also attached a odf of the diagram of the architecture mannualy)
- Agent 0 (Outreach): finds missing records and writes email drafts
- Agent 1 (Extractor): reads PDFs and extracts structured JSON data
- Agent 2 (Timeline): builds chronological health narrative
- Agent 3 (Conflict Detector): finds contradictions and gaps
- Agent 4 (Reporter): writes final report and generates graph
- RAG: ChromaDB + HuggingFace for question answering across all reports
- Orchestrator: LangGraph connects all agents with shared state