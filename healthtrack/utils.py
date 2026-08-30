import time 
import logging 


# shared logger for the whole app replaces print() statements  with timestamped  messages (info/warning/error) that are easier to read 
logging.basicConfig( level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('healthtrack')
llm_call_count = 0

#here we gonna implement a retry wrapper around every llm call if llm fails due network issues 
#or rate limit it retries up to 3 times , wait time double each attempt :1s then 2s then 4s
#its exoponential backoff, if all 3 attempts fails the error it raise the error 

def call_llm(chain,payload,retries=3): #payload  the dictionary with the variables to fill in the prompt
    global llm_call_count
    start=time.time() #record the time before we start trying, so total time includes retries not just the last try

    for attempt in range(retries):

        try:
            response=chain.invoke(payload)  #try to call the llm  if it work return the response immediately
            elapsed=time.time()-start #how long the whole call took including any retries
            llm_call_count+=1 #increase the global counter every time a call actually succeeds
            logger.info(f"llm call succeeded in {elapsed:.2f}s (total calls this run: {llm_call_count})")
            return response
        except Exception as e:     #if llm fails for any reason catch the error as e
            if attempt==retries-1:   #if it fails the range of tries go from 3 to 2....
                logger.error(f"llm call failed after {retries} attempts: {e}") #all retries failed, log it as an error before raising
                raise #all retries failed raise an eroor 
            wait=2**attempt #attempt0=1s , attempt1=2s , attempt2=4s how long to wait before retrying

            logger.warning(f"llm call failed attempt {attempt+1} retrying in {wait}s: {e}") #warning not error because we're still retrying, not fully failed yet
            time.sleep(wait) #pause the program for wait seconds before the next attempt

#before If the LLM fail for any reason: network timeout, groq rate limit, internet drops for 1 second the whole pipeline crashe immediately with an ugly error.

#now instead with exponential backoff:
#attempt 1 fail then

