import time 

#here we gonna implement a retry wrapper around every llm call if llm fails due network issues 
#or rate limit it retries up to 3 times , wait time double each attempt :1s then 2s then 4s
#its exoponential backoff, if all 3 attempts fails the error it raise the error 

def call_llm(chain,payload,retries=3): #payload  the dictionary with the variables to fill in the prompt

    for attempt in range(retries):

        try:
            return chain.invoke(payload)  #try to call the llm  if it work return the response immediately
        except Exception as e:     #if llm fails for any reason catch the error as e
            if attempt==retries-1:   #if it fails the range of tries go from 3 to 2....
                raise #all retries failed raise an eroor 
            wait=2**attempt #attempt0=1s , attempt1=2s , attempt2=4s how long to wait before retrying

            print(f"llm call failed attempt {attempt+1} retrying in {wait}s_{e}")
            time.sleep(wait) #pause the program for wait seconds before the next attempt

#before If the LLM fail for any reason: network timeout, groq rate limit, internet drops for 1 second the whole pipeline crashe immediately with an ugly error.

#now instead with exponential backoff:
#attempt 1 fail then wait 1 second try again
#attempt 2 fails then wait 2 seconds try again.........
#Instead of crashing on the first failure it give the network a chance to recover

