import os 
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from prompt_engineering import tutor,translator,analyst  #i will reuse the same prompt built 
#in prompt engeneering file 

#now lets build one bot for the personas in the file prompt_angineering do this 
#bot allow us to swith between personas when we ask him to do that and 
#il will make it with streaml lit to do an itreactive intrface 

#bot pre_loaded with my specific engineered personas (Tutor, Translator, and Analyst)
# that i already did the prompt for each persona 

load_dotenv(".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY"))
def ask_persona(persona,question): #same function 
    response=client.chat.completions.create(model="llama-3.3-70b-versatile",
                                            messages=[{"role":"system","content":persona},#
                                                      {"role":"user","content":question}])
    return response.choices[0].message.content 


#lets creat a bot class (reusable object )oop

class MultiPersonaBot:
    def __init__(self):#my imported prompt are stored in the object automatically
        self.personas = {
            "tutor": tutor,
            "translator": translator,
            "analyst": analyst }
    def chat(self, persona_name, question):
        if persona_name not in self.personas:
            return f"Persona '{persona_name}' not found"
        return ask_persona(self.personas[persona_name], question)#in case the user chose a persona that i already saved likr tutor for 
    
#st user interface-------------------------------------------------------
st.title("multi persona bot ")
st.markdown("choose a persona, ask him a question, and let him respond to your question")

bot=MultiPersonaBot() #it automatically loads the oop and the if loop inside of it and load also the personas with thei prompts
selected_persona = st.selectbox(" choose an AI persona:", ["tutor", "translator", "analyst"]) #creates a  clickable dropdown box containing three choices
user_query = st.text_area(" Enter your question here:") #creat a box where the user can write his question 

if st.button("Ask Bot"): #its a button by default its false and if the user click it streamlit go to my python code and run it
    if user_query != "":
        #call class method
        response = bot.chat(selected_persona, user_query)
        st.success("Here is your answer:")
        st.write(response)
    else:
        st.warning("please type something ")