#now we rewrite the imports after setting up correctly the cong.py 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
import pdfplumber
import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model
#cannot run it directly from python as a script we should run it as a modul because we have the 
# path and tha api and the model in the config file and we imported everything from there

#agent 1 extractor agent: job: reay every pdf and extract structured health data from each one 
#taked folder path where all pdf are stored then reads pdf with pdf plumber then passes each text 
#to LLM that will excract important medical facts and return a list of dict (one dict per report)
#so next the agent is able to work with strutured data 
#why we must use structured data here? because timline agent need to sort by date 
#and conflict agent need to compare values across reports 

extractor_prompt=ChatPromptTemplate.from_messages([
("system", """ you are an expert data exctractor 
 extract key information from this medical report and return only JSON object,
 ps: no extra text or explanation just the  JSON:
 JSON format:
     {{"clinic": "clinic name",
        "date": "YYYY-MM-DD",
        "doctor": "doctor name",
        "findings":
      {{"blood_pressure": "value or null",
        "glucose": "value or null",
        "cholesterol": "value or null",
        "weight": "value or null"}},
        "diagnosis": "main diagnosis",
        "medications": "medications or none",
        "notes": "any important notes"}}
 if a value is not mentioned write NA"""),
 ("human","{report_text}")]) #report text get filled with the raw text exctraced from the pdf 

#connect the excractor prompt with the llm 
extractor_chain=extractor_prompt|llm

#lets build a fuction to read pdf that take in input folder path as a str and return a dict 
#why it does return a dict ? first return a dict where the key is file name and the value is the raw text 
#so like that we can keep track and know each task from which pdf came 
def readPDFS(folder_path:str)->dict:
    raw_texts={}      # empty dict to save raw text excracted from pdfs 
    for filename in os.listdir(folder_path):#os.listdir return a list of every file name in the folder 
        if filename.endswith(".pdf") or filename.endswith(".txt"):#look for pdf files or text files only 
            file_path=os.path.join(folder_path,filename) #create the file path to be able to open it 
            
            if filename.endswith(".pdf"):
                with pdfplumber.open(file_path) as pdf: #loop through every page of the pdf extract the text from each page join all pages into one big string separated by newlines
                    text=".\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            else:    #it's not a pdf it's a txt 
                with open(file_path,"r") as f:
                    text=f.read()
            raw_texts[filename] = text #save the excrated texts into the dict raw_texts
            print(f"read{filename}")
    return raw_texts

#not lets build the exctractor agent function that take the folder path as an input and return a list of dict 
#where we gonna get one dict of report 
def extractor_agent(folder_path:str)->list:
    raw_texts=readPDFS(folder_path) #call the function built before and return all a dict with the key as file name and the value as the texts 
    extracted_data=[]  #empty list where we gonna collect all the structured data of the reports 

    for filename, text in raw_texts.items():    #.items() loops through the dictionary and return both key and value 
        print(f"agent is exctracting data from {filename}....")
        response = extractor_chain.invoke({"report_text": text}) #send the raw data of each file to the LLM the LLM read it and return a JSON with the structured data
        clean = response.content.strip() #remove any exta spaces the LLM added around the JSON
        clean = clean.replace("```json", "").replace("```", "").strip() #remove backticks becaus somtimes LLM return a markdown formatiing 
        
        # convert JSON string to python dictionary
        try:
            data =json.loads(clean)
            data["source_file"] = filename
            extracted_data.append(data)
        except:
            # if JSON parsing fails save raw text so nothing is lost
            extracted_data.append({"source_file": filename, "raw_text": text})

    return extracted_data

#test (it only run for this file but this block will not run if imported)
if __name__ == "__main__": #removed (c:user\lenovo\.....)
    # import the sample folder path from config so it works on any computer
    from healthtrack.config import SAMPLE_DIR
    # run the extractor on the sample reports folder
    results = extractor_agent(str(SAMPLE_DIR))
    # print each extracted report
    for r in results:
        print(r)


# in simple words this agent read every pdf and txt file from the folder
# saves the raw text in a dict where key=filename and value=raw text
# then loops through that dict and for each file sends the raw text to the LLM
# the LLM read it and returns clean structured JSON with only the important medical facts
# we parse that JSON into a python dict and add it to a list
# at the end we return a list of clean dicts — one per report — ready for the next agent

