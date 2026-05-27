from groq import Groq
from dotenv import load_dotenv
import os 
load_dotenv()
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

messages=[] #made this list as the chatbot memo
while True:
    user_input = input("You: ")
    
    if user_input == "/exit":
        print("Bye")
        break
    elif user_input == "/clear":
        messages = []  # reset conversation history 
        print("Conversation cleared")
        continue
    elif user_input == "/help":
        print("/exit - quit the chatbot")
        print("/clear - clear conversation history")
        print("/help - show commands")
        continue
    messages.append({"role": "user", "content": user_input}) #to memorize the input (user prompt)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.9,
        messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply}) #to memorise the output (ai reply)
    
    print(f"AI: {reply}")

    #first i did imported groq and the api and loaded it the connected it whith groq then 
    #did the while loop here just in case the user enterd on of these command and i mean by that if he didn'nt
    #typed a normal prompt (example:"what is the average age in italy ")
    #if the user wrore a normal prompt (that dosent include exit help or clear) 
    #first i save the user input in a list then a create a chat complection that take the user input 
    #saved in messages and pass it to the variable messges in client.create.complection 
    #then take the first api complection (ai response ) and print it the save it in messages list 
    
    #so this is a chat bot with memory 
    #and when i wanted to msave the input to messages by using append i made him understand that this is the 
    #user message and when i wanted to save ai output i used memories append and made him understand that 
    #this is the ai assistant message 

