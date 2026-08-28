#now we rewrite the imports after setting up correctly the cong.py 
#so here the import and folder path and loading the api 
#and using it and specifiyin the model gonna look much cleaner since we have them defined 
#in config.py 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
from healthtrack.utils import call_llm
from langchain_core.messages import ToolMessage

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

#now for the rest of the code gonna be equal we just changed the imports 
#the way of specifiying the file path loading the api and specifiying the model

#agent 0: outreach_agent
# runs before all other agents
# two scenarios it handle:
# scenario A: user uploads PDFs we extract text and pass it here
# scenario B : user just types their medical history in text
# in both cases the agent does the same 3 things:
# 1_ identify all providers mentioned
# 2_ infer what providers are "probably" missing based on medical logic
# 3_ write email drafts  request those missing records

#--------------------------------------------------------------------------------
#added thif function tool to look up the medical records request contact email for a clinic hospital or doctor
#in   a real system this would call a web search api for now we use common email patterns based on 
# the provider name , the ll decide when to call this 



@tool  #@ tool is a dectatore that wraps the function and register it  as a tool  that the llm can call
       #without this  def lookup_provider_contact is just a regulare py funct not a tool that llm can use automatically

def lookup_provider_contact(provider_name: str) -> str: 
    """takes provider name as an input ex:"chicago clinic " and return an email adress for it """
    name_lower = provider_name.lower().replace(" ", "") #converts "Chicago Clinic" to "chicagoclinic" so we can build email patterns from it
    patterns = [f"records@{name_lower}.com",    
        f"medicalrecords@{name_lower}.org",             #3 common email patterns 
        f"info@{name_lower}.com"]
    return f"suggested contacts for {provider_name}: {', '.join(patterns)}"
llm_with_tools = llm.bind_tools([lookup_provider_contact])   #tell llm that he have access to this tool without this llm dosent 
                                                             #even know that this tool exists 



outreach_prompt=ChatPromptTemplate.from_messages([
("system", """ you are a medical record assistant
 you have access to a lookup_provider_contact tool use it to find contact emails for every provider you identify
 your job is to help patients to collect all their medical records.
given either uploaded PDF text OR a described medical history:
 
 -identify all clinics hospitals and doctors visited 
 -infer any missing providers the patient should have seen (example: high blood pressure then should have seen a cardiologist)
 -find their medical records request email address (use common patterns like records@[clinicname].com or medicalrecords@[hospital].org)
 (or try to get the email visiting clinic, hospital , doctor website)
 -write a professional email  requesting medical records for the patient
 -note:Generate ONE email per provider

format your response exactly like this:
 
PROVIDERS VISITED:
- [provider name]

MISSING PROVIDERS:
- [provider name] - [reason why needed]

EMAIL DRAFTS:
To: [provider name]
Subject: Request for medical records
[email body]

--- next email ---
To: [next provider]"""),
("human", "{user_input}")]) # {user_input} is the blank that gets filled with whatever the user provide(pdfs or text)

#connect prompt to model 
outreach_chain = outreach_prompt | llm_with_tools  #the chain needs to use llm_with_tools not just llm 
                                                   #otherwise the tool is registered but never actually available when the chain runs



#outreach agent function 
def outreach_agent(user_input: str) -> str:
    print("agent 0: analyzing medical history and looking up provider contacts...")

    #before we just did outreach_chain.invoke with a dict {"user_input":...} but that dosent let us
    #append messages later, so instead we filled the prompt with the user_input 
    # build the actual message list from the prompt first using 
    #to_messages() that turns the prompt template into a real list of message objects(2 objects 
    # systemmessage and user message) 
    
    #why we turn the prompt into a list ?  we need to add more messages to it later (the tool call, then the tool result) 
    #  a finished prompt can't be added to, but a list can.
    messages = outreach_prompt.invoke({"user_input": user_input}).to_messages()

    #send the message list (not the chain) to call_llm becuse we need llm_with_tools directly
    #this way response comes back as an actual AIMessage object with tool_calls attached to it
    response = call_llm(llm_with_tools, messages)

    #check if the llm decided to call the lookup_provider_contact tool
    #hasattr checks if the response object has a tool_calls atribute
    #response.tool_calls is a list of tool calls the llm wants to make
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"tool called: {len(response.tool_calls)} provider lookups made")

        #this is the part we had wrong before: we used to just paste the tool result as text
        #into the next human message, but the llm cant actually tell that came from a tool call
        #it just sees it as more user text, so the protocol was technically broken even tho it worked
        #the correct way is to append the ai's own message (the one with tool_calls in it) first
        #so the conversation history actually shows "i decided to call this tool"
        messages.append(response)

        for tc in response.tool_calls:  #loop through each tool call the llm made
            #actually run the tool with the provider name the llm passed
            result = lookup_provider_contact.invoke(tc["args"])
            print(f"looked up: {tc['args']['provider_name']}")

            #now instead of pasting this into text we wrap it in a ToolMessage
            #tool_call_id is what links this specific result back to the specific call the llm made
            #this matters more when there is more than one tool call at once, so the llm knows
            #wich result belongs to wich provider it asked about
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

        #call the llm again but now with the full history: original question + ai tool call + tool results
        #this is the real tool-role protocol, the same one we used on day 11 before we accidently
        #simplified it into string concatenation during the refactor
        final_response = call_llm(llm_with_tools, messages)
        return final_response.content  #return the final response that includes the tool results

    #if the llm didnt call any tool just return the response directly
    return response.content

# Test                                (it only run for this file but this block will not run if imported)
if __name__ == "__main__":
    # Test with medical history
    result = outreach_agent("Patient has diabetes and high blood pressure visited Chicago Clinic in 2022.")
    print(result)

#changelog for this file:

#1_ changed outreach_chain.invoke({"user_input": user_input}) to call_llm(outreach_chain, {"user_input": user_input})
#   before this if groq fail while outreach agent is running the whole pipeline crashes at agent 0
#   before even starting the analysis, after this change it retries 3 times with exponential backoff
#   so now this agent is more robust to network failures

#2_ added @tool and lookup_provider_contact so llm can actually call a real function to find provider emails
#   added llm_with_tools so llm knows the tool exists and can use it
#   changed chain to use llm_with_tools insted of just llm otherwise the tool is registerd but never
#   actually available when the chain runs
#   added tool instruction to system prompt so llm knows wen to use it
#   upgraded outreach_agent to check for tool calls run them and send results back to llm

#3_ fixed the tool-role protocol: removed the part where we pasted tool results as plain text into
#   user_input, that was never the real protocol it just happend to work becuse groq is lenient about
#   message structure. now we build a proper message list and append the ai's own message + a
#   ToolMessage per tool call, this is more correct becuse the llm can actually see wich message
#   came from wich role insted of guessing based on text content, and it matches wat we did
#   originaly on day 11 before this got lost somwhere during the wp5/wp6 refactor