from pathlib import Path 
import os 
from dotenv import load_dotenv 

load_dotenv()

#here in this file we gonna put all important informations about where files are 
#in this file 
#before we had c:/lenovo/... writteen in many diffrent files 
#and if someone else took the code to run it on another compture it will not work 
#now we have all pathes and secret key here so every other file should ask config.py 
#to get the path and the info that he need 


# Path(__file__) = this file (config.py)
# .resolve() = get the full path
# .parent = go up to healthtrack/
# .parent again = go up to AI-Agents-Internship/ (project root)
BASE_DIR=Path(__file__).resolve().parent.parent
#so no matter where the project is installed BASE_DIR always know where the root is 

DATA_DIR   = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
SAMPLE_DIR = DATA_DIR / "sample_reports"

#now nuilded all other path starting and using BASE DIR  so now we don't have no more 
#hardcoded c:/lenovo/... anywhere else 


#create folder automatically if the dosent exista already 
for d in (UPLOAD_DIR,CHROMA_DIR,SAMPLE_DIR):
    d.mkdir (parents=True,exist_ok=True)

#where we loop folders and is a folder dosent exist we create it using (mkdir)
#and we have parents=True where we should create any missing parent folder exist_ok dosent crash 
#if the folder dosen't exists 

#store setting (llm and models ) in one place 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("No API key found , create a new.env file , for instructions check .env.example")
LLM_MODEL    = "llama-3.3-70b-versatile"
EMBED_MODEL  = "all-MiniLM-L6-v2"
#the reason defining all these model onve here i this file is because if i want to change them i can 
#change it once from these file instead of changing it in every file that i used this models for 