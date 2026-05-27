from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
client=Groq(api_key=os.getenv("GROQ_API_KEY")) #connect with groq
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    messages=[{"role": "user", "content": "create a completly new basketball play and describ him to me in two lines"}])
print(response.choices[0].message.content) 
#the response of the API could be a list of complections(answers) 
#so i want the first item of that list 
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.9,
    messages=[{"role": "user", "content": "create a completly new basketball play and describ him to me in two lines"}])
print(response.choices[0].message.content)

#here we can see the difference between an AI model with temperaure 0.3 and 0.9
#0.3 : the ai is precise and predictable and say facts
#0.9 : is more creative and give original and unexpexted answers 


#I can call groq in diffrent ways just by changing the value of content 
#key for rxample i can put "content":"I'm bored tell me a story"