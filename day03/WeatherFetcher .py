#just was thinking about the logic of doing a weatherfetcher 
#what i need to do is when the user enter the name of the city 
#my code can convert it to the coordinates for the exact same location 
#that the user choose then i take this coordinates and push them throup 
#an http get and take the url from open meteo to provide meteo information 
#for the user on the location that he chose 

import requests
#i could've use a simple function to do the fetcher but i prefered to use a class 
#so in the future if we want to ad for exemple wanna do a fetche for weather 
# and population numer for that city  get_population i can add any other function 
#i can put it inside of class
class weatherFetcher:

    def __init__(self,city):
        self.city=city
        
    def get_weather(self):
        try:
           geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
           geo_response=requests.get(geo_url)
           geo_data=geo_response.json()

           if "results" in geo_data:
            first_result=geo_data["results"][0] #because in geo data output I get a list of resulats

                                                #because I can have the same name of the city in two diffrent countries her I'm assuming that

                                                #the first city in the result is ehat the user wants and as I said results is a list and every results

                                                #is a dictionary per se
            latitude=first_result["latitude"]
            longitude=first_result["longitude"]
            print(f"if found the coordinations for  {self.city}:latitude={latitude},longitude={longitude}")
            meteo_situation=input(f"now that I found the city cordination print 'Yes' if you want the meteo situation in {city} ")

            if meteo_situation.lower()=="yes":
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code&timezone=auto"
                weather_response=requests.get(weather_url)
                weather_data=weather_response.json()
                current_weather=weather_data["current"]
                temperature=current_weather["temperature_2m"]
                time=current_weather["time"]
                print(f"the current temperature in {self.city} is {temperature}°C")
                print(f"the current time in{self.city} is {time}")       
           else:
              print(f"{self.city} not founf please check the spelling")
        except requests.exceptions.Timeout:
                      print("Request timed out")

city = input("Enter city name: ")
fetcher = weatherFetcher(city)
fetcher.get_weather()


