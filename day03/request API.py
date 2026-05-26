import requests

#url for zahle 
url="https://api.open-meteo.com/v1/forecast?latitude=33.8468&longitude=35.902&hourly=temperature_2m&current=temperature_2m,weather_code&timezone=auto"
#the API is: https://api.open-meteo.com/v1/forecast and the rest of the url are the 
#parameters for the location that I chose 

response1=requests.get(url)
data=response1.json()  #open meteo default data format 

response1.status_code
             

# extract some of these data for example
current=data["current"]  #is a key in zahle dictionary that has value a dictionnary (nested dict)
print(f"Time: {current['time']}")  #is the ey inside the nested dict current 
print(f"Temperature: {current['temperature_2m']}°C")


#since on open meteo i can do only get http now i will use a website where i can 
#practice hhtp request and do an example of an post request (asked chat gpt how i can practice post 
#http and gave me httpbin.org)

url="https://httpbin.org/post"

#jason format 
data={"name":"elias","city":"zahle"}

response= requests.post(url,json=data)
result=response.json()
print(result["json"])

#handling errors 
try:
    response = requests.get("https://httpbin.org/status/404", timeout=2)
    response.raise_for_status() 
    print("Success")
    
except requests.exceptions.Timeout:
    print("Request timed out")
    
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")
