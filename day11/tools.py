import os 
import sys
import requests
from groq import Groq
from dotenv import load_dotenv
import json 

#so here we gonna make sure that the LLM can call a function bcs for example llm
#dosent know how to do for example addition so i should make an 
#addition function and make hime use it to give the user an answer (LLM is just a text generator)
#so my function is like a small brain that im passing to llm and that brain tell 
#him exactly what to do 


#add
def add(a:float,b:float)->float:
    """   adds two numbers together   """
    return a+b
#substract 
def substract(a:float,b:float)->float:
    """   substracts two numbers"""
    return a-b
#multiply
def multiply(a:float,b:float)->float:
    """   multiply two numbers"""
    return a*b
#divide
def devide(a:float,b:float)->float:
    """  divide two numbers and handle division by zero"""
    if b==0:
        return "erro :division by zero"
    return a/b


#weather tool reusing day 3 weather fetcher (i tried to import day 3 weather )
#wasnt able to do it! so copied weatherfetcher class that i used in day 3 (removed the input function that was
# in the class weather fetcher because the LLM cannot type in the terminal a response to the in put so 
# we must remove it to get automated )  
class weatherFetcher:

    def __init__(self,city):
        self.city=city
        
    def get_weather(self):
        try:
           geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={self.city}&count=1&language=en&format=json"
           geo_response=requests.get(geo_url)
           geo_data=geo_response.json()

           if "results" in geo_data:
            first_result=geo_data["results"][0] 

            latitude=first_result["latitude"]
            longitude=first_result["longitude"]
            print(f"if found the coordinations for  {self.city}:latitude={latitude},longitude={longitude}")
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code&timezone=auto"
            weather_response=requests.get(weather_url)
            weather_data=weather_response.json()
            current_weather=weather_data["current"]
            temperature=current_weather["temperature_2m"]
            return f"The current temperature in {self.city} is {temperature}°C"
                   
           else:
              print(f"{self.city} not founf please check the spelling")
        except requests.exceptions.Timeout:
                      print("Request timed out")

def fetch_weather_tool(city: str) -> str:
    """fetch the current weeather temperature for any city"""
    fetcher = weatherFetcher(city)
    return fetcher.get_weather()

#connect the previous tools that i built with LLM (for add an weatherfetcher).json
#i can add substract and multiply and divide in the same way 
load_dotenv(".env")
client=Groq(api_key=os.getenv("GROQ_API_KEY"))

tools=[{"type":"function","function":{"name":"add",
                                      "description":"adds two numbers together",
                                      "parameters":{"type":"object",
                                                    "properties":{
                                                        "a":{"type":"number","description":"first_number"},
                                                        "b":{"type":"number","description":"second_number"}},
                                                         "required":["a","b"] }}},
        {"type":"function","function":{"name":"fetch_weather_tool",
                                       "description":"Use this tool ONLY when the user explicitly asks for the current weather, temperature, or climate conditions of a city",
                                       "parameters":{"type":"object",
                                                     "properties":{
                                                         "city":{"type":"string","description":"city name"}},
                                                         "required":["city"]
                                                         }}} ]


#map the tool name into python function 
funct={"add":add,"fetch_weather_tool":fetch_weather_tool}

def smart_assistant(user_message):
    messages=[{"role":"user","content":user_message}]

    response=client.chat.completions.create(model="llama-3.3-70b-versatile",
                                            messages=messages,tools=tools, #passing the tools that are saved in functions to LLM andd he use it when need it 
                                            tool_choice="auto") #LLM choose which tool he gonna use based on the user input
    msg=response.choices[0].message
    messages.append(msg) #adedd LLM's tool request to our conversation history



    #did LLM decided to call the tool ?if yes what it is the tool he used 
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            tool_name=tool_call.function.name
            args=json.loads(tool_call.function.arguments)
            result=funct[tool_name](**args)#call the actual python function 
            print(f"the tool is called {tool_name},and the result is {result}")
            #Send the result into the conversation history with the tool role
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": str(result)
            })
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages)
        return final_response.choices[0].message.content
    return msg.content #if no tool needed return the LLM response 


print(smart_assistant("what is 15 + 27?"))
print(smart_assistant("what is the weather in Beirut?"))
print(smart_assistant("what is the capital of France?"))
