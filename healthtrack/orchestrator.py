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
from healthtrack.agents.outreach import outreach_agent
from healthtrack.agents.extractor import extractor_agent
from healthtrack.agents.timeline import timeline_agent
from healthtrack.agents.conflict import conflict_agent
from healthtrack.agents.reporter import reporter_agent

# import the upload folder path from config so we know where to read files from
from healthtrack.config import UPLOAD_DIR

import os

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

def run_pipeline():
    print("_"*50)
    print("starting healthtrack pipline")
    print("_"*50)
    #read all pdfs from the upload folder once 
    print("\n reading pdfs")
    raw_texts=read_file(str(UPLOAD_DIR)) #used the function that we did before that take the file 
                                        #path where all files are read every file 
                                        #and store it in a dict wehre key =file name 
                                        #and value =content (raw_text)
                                        #and return raw_text 
                                        #so here we saved the content in the raw text variable 
                                        #to pass it between agents
    #run outreach agent ,takes all text combined and find missing provider and genreate email draft
    print("outreach agent ....")
    all_text="\n".join(raw_texts.values())
    outreach_result=outreach_agent(all_text) #outreach agent funct in outreach agent file
    print("outreach done ")

    #run exctractor agent, # it takes the raw text dictionary and extracts structured data
    print("extractor agent ...")
    extracted_data=extractor_agent(raw_texts)  #exctractor agent function that we have in extractor file
    print(f"extracted {len(extracted_data)} reports")

    #timline agent , it takes structured extracted data and build a chronological narrative
    print("timline agent ...")
    timeline=timeline_agent(extracted_data) #we used the imported timline agent funct imported from timline file 
    print("timline done ")

    #conflict agent it takes timline and extracted data to find contradictions 
    print("conflict agent ")
    conflicts=conflict_agent(timeline,extracted_data) #used conflict agent funct that we imported from conflict file 
    print("conflict agent done ")

    #reporte agent  ,it takes evrything and generate the final report and graph 
    print("reporter agent ....")
    reporter ,fig= reporter_agent(timeline,conflicts,extracted_data)
    print("report done")
    

     # return all results in a dictionary so we can use them later
    return {"raw_texts": raw_texts,
        "outreach_result": outreach_result,
        "extracted_data": extracted_data,
        "timeline": timeline,
        "conflicts": conflicts,
        "report": reporter,
        "figure": fig}

# this block runs only when we execute this file directly
# it runs the pipeline and prints the final report
if __name__ == "__main__":
    results = run_pipeline()
    print("_"*50)
    print("FINAL REPORT:")
    print("_"*50)
    print(results["report"])



# the old orchestrator used langgraph with nodes edges and a typeddict it was more complex than what we needed for a linear pipeline
# the new orchestrator is simplerit just calls each agent in order and passes data directly no graph no nodes 

#the new one is better bcz we havae simpler code is easier to read debug and fixlanggraph is useful for loops and branching but our pipeline is a straight line
# the old code also read pdfs multiple timesthe new code reads everything once at the start and passes it aroundthis is faster and cleaner
#and also here no hardcoded path c:\lenovo\....

