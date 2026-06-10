import streamlit as st
from ResearchHelper import conversation,quiz,compare,summarize

st.title("🕵️‍♀️ Hello ,I'm Your Reseach Helper ")
st.markdown("ask my anything and I'll search it for you ")

#session state 
#First time the app loads messages doesn't exist so  create it as empty list. Second time it already exists  skip dont reset it
if "messages"  not in st.session_state:
    st.session_state.messages=[]

if "last_topic" not in st.session_state: #if the user didnt reserch anything yet = empty str 
    st.session_state.last_topic=""


# display chat history
#because st rerun the whole file on every click without this loop every time  clicked a button all previous messages disappear from the screen
for msg in st.session_state.messages: #go throug messages one by one 
    with st.chat_message(msg["role"]):  #like opening a chat buble (user, assistant)
        st.write(msg["content"])      #put the message of user/asisstent here (in content)


#chat input 
user_input=st.chat_input(" research any toic you want ")

if user_input:           #if user input exists
    st.session_state.last_topic=user_input    #add his imput as the leatest reseach
    st.session_state.messages.append({"role":"user","content":user_input}) 

    with st.chat_message("user"): #if the role is user 
        st.write(user_input)      #insert user input in "content"
    
    with st.chat_message("assistant"):  #if role=assistent
        response=conversation.invoke(              #call the converation variable that have #RunnableWithMessageHistory that have in it the chain with the model and the prompt with memory saving  
             {"input":user_input},
             config={"configurable":{"session_id":"research_session"}})    
        st.write(response.content)
        st.session_state.messages.append({"role":"assistant","content":response.content})
       
# show tool buttons only after first message and run the tool that the user picked 
if st.session_state.last_topic !="":     #if the first message exists
    st.markdown("what do you wnat me to do next ")
    col1,col2,col3=st.columns(3)

    with col1:
        if st.button("📝 Summarize"):
            st.session_state.messages.append({"role": "assistant", "content": summarize.invoke(st.session_state.last_topic)})
            st.rerun()
    with col2:
        if st.button("❓ Quiz me"):
            st.session_state.messages.append({"role": "assistant", "content": quiz.invoke(st.session_state.last_topic)})
            st.rerun()
    with col3:
        if st.button("⚖️ Compare"):
            second = st.text_input("compare with what?")
            if second:
                st.session_state.messages.append({"role": "assistant", "content": compare.invoke(f"{st.session_state.last_topic} vs {second}")})
                st.rerun()


#when button clicked?
#1 run the tool
#2 save result to messages
#3 rerun streamlit to redraw the chat
#Compare is the only different one because it needs a second topic from the user first..


