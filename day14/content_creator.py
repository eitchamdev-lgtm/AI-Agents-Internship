import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv,find_dotenv
import os 

load_dotenv(find_dotenv())
llm=ChatGroq(api_key=os.getenv("GROQ_API_KEY"),model="llama-3.3-70b-versatile")

# original version had 2 agents: researcher + writer
# upgraded version has 3 agents: researcher + writer + editor
#here's the apgraded of the multiagent_intro here i decided to do a content creator:
# 1_ added a 3rd agent (editor)  writer writes, editor clean it
# 2_ kept researcher the same(same prompt) added style parameter to writer same notes, different article based on user choice
# 3_ wrapped everything in streamlit UI

#--------------------------------------------------------------------------------------------
#agent1: researcher prompt:
researcher_prompt=ChatPromptTemplate.from_messages([
    ("system",""" you are an expert researcher.
     your job is to research a topic and produce a well structured notes that  include:
     -main concept explained simply 
     -5 key facts
     -important statistic or number if rilevant 
     -current trend 
     -potential future developpment
     keep it factual structured and detailed"""),
     ("human","{topic}")])

#let's connect the researcher prompt with our model
researcher_chain=researcher_prompt|llm

#let's build a simple researcher function that we can call with the topic and that return 
#the model (agent) the notes 

def researcher_agent(topic:str)->str:
    print(f"researcher working on {topic}")
    response=researcher_chain.invoke({"topic":topic})
    return response.content

#--------------------------------------------------------------------------------------------------
#agent2 : writer prompt 
#upgraaded: now accepts style parameter 
#same notes of the researchet but this write return a completely diffirent output depends on the style chose 
#reusable prompt with two variables {style},{research_notes}
writer_prompt=ChatPromptTemplate.from_messages([
    ("system",""" you are an expert writer 
     your job is to take research notes and write a full article in this style:{style}
     style guide:
     -accademic: structured, formal  and grammatically correct 
     -journalist: news article style , punchy opening 
     -simple. explain like your explaining to a 5 years old, shorts sentences
     include : engaging introduction, clear topics with headers , strong conclusion """),
     ("human","write an article based on these research notes:\n{research_notes}")]) #passing the research notes as an input to the writer


#writer chain 
writer_chain=writer_prompt|llm

#let's build a writer function that takes two inputes {style} and {research_notes} and run it 
def writer_agent(research_notes:str,style:str)->str:
    response=writer_chain.invoke({"research_notes":research_notes,"style":style})#in the invoke we pass a dict , langchain reads the dict 
    #and for the key "style" find box labeled {style}  and fill it eith the styke that the user chose 
    return response.content

# writer_chain has the prompt and llm connected
# when i call .invoke() i pass a dictionary with two keys: style and research_notes
# langchain matches each key to its {variable} in the prompt and fills it
# now the prompt is complete with the style the user picked and the notes from the researcher
# langchain sends the complete prompt to the LLM and the agent writes the article


#-----------------------------------------------------------------------------------------------------
#agent3: editor prompt 
#new agent adedd here , writer focus on structure editor focus on quality (already explained befor how this resusable prompts work)
editor_prompt=ChatPromptTemplate.from_messages([
    ("system",""" your are an expert editor 
     your job is to take an written article and polish it by :
     -fixing any akward sentences
     -improving flow between sections
     -makinng the intro and the conclusion stronger 
     keep the original structure and meaning the same , return the improved article """),
     ("human","edit and improve this article:\n{article}")])

#editor chain
editor_chain=editor_prompt|llm

#editor function that take article as an input and return the improved article 
def editor_agent(article:str)->str:
    response=editor_chain.invoke({"article":article})
    return response.content


# ----------------ORCHESTRATOR--------------------
#connect all three together , the first research the the output that we got ffrom 
#it we pass it to the writer the writer write a full article with the style that the user chose 
#the editor takke the writer output as an input polish it and return the imporoved clean article 
#we connect them together using a function that get topic of the research and style of the article as in input
# #because the user decides the topic and the style and return a dictionnary { "topic": topic, "research_notes": research_notes,"article": polished_article} 

def content_creator(topic:str,style:str)->dict:
    research_notes=researcher_agent(topic) #save the output of the researcher agent function that have the topic decided in it we save it in the variable reserch_notes
    article=writer_agent(research_notes,style)#call the writer_agent function pass to it the researcher output(notes), and the syle and save it into article variable 
    polished_article=editor_agent(article)#take the article reterned by the writer agent pass it to the editor agent function and save it into polished_article variable 
    return { "topic": topic,"style": style, "research_notes": research_notes, "article": polished_article}#return the dictionary and pass the variables saved before to the keys of this dictionary 

#---------------------------------------------------------------------------------------------------------
#streamlit UI 
st.title("📝 ContentCreator")
st.markdown("pick a style choose a topic then I'll research the topic write it and polish it for you ")


#style 
st.markdown("what style do you want ")
style=st.radio(label="style",options=["🎓 Academic", "📰 Journalist", "🎯 Simple"],horizontal=True)

#its a radio button that allow the user to use an option from a list of options 
#the first argument is the label shown to the user
#the second argument is a list of options

#topic input 
topic=st.text_input("hat topic should the article be about ")
if st.button("create an article"):
    if topic.strip()=="":                     #if the user clicked creat article without typing a topic
        st.warning("please enter a topic first")
    else:
        style_clean=style.split(" ")[1] # style radio returns the full string ex:"🎓 Academic" but we only need the word "Academic"
                                       # so we split it by space which gives us ["🎓", "Academic"] and we take index [1] = "Academic"
        #create two columns side by side left research and right for article
        col1,col2=st.columns(2)

         # left column: researcher agent runs and returns the notes then we show them in a collapsible section
        with col1:
            with st.spinner("🔍 Researcher working..."): #run animation while waiting 
                research_notes = researcher_agent(topic) #agent 1 runs 
            st.success("research done ")
            with st.expander("view research notes"):  # collapsible section user can open or close
                st.write(research_notes)

        # right column: writer takes the notes and writes the article then editor takes the article and polish it
        with col2:
            with st.spinner(f"writer working in {style_clean} style..."):
                article = writer_agent(research_notes, style_clean)     #agent 2 runs
            with st.spinner("editor polishing the article..."):
                polished_article = editor_agent(article)                #agent 3 runs 
            st.success("article ready")

        # show the final polished article below both columns with a line separator
        st.markdown("---")
        st.markdown(f"### 📄 Final Article — {style} style")
        st.write(polished_article)

        # download button so user can save the article as a txt file
        # topic[:30] means we take only the first 30 characters of the topic as the file name
        st.download_button(label=" Download Article",
            data=polished_article,
            file_name=f"{topic[:30]}_{style_clean}.txt", # first 30 chars of topic as filename
            mime="text/plain")

