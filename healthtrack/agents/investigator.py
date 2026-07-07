from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
from healthtrack.utils import call_llm

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

# investigator agent only runs when conflicts are found
# job: take the contradictions from conflict agent and dig deeper into each one
# it asks why did this contradiction happen and what should the patient ask their doctor
# this agent only exist becaus of the conditional branch we added in orchestrator if no conflicts found this
#  agent never runs and we skip straight to reporter this is what makes the pipeline agentic the system decides the path not us

investigator_prompt = ChatPromptTemplate.from_messages([
    ("system", """you are a medical investigator
     you receive contradictions and gaps found in a patients medical records
     for each one provide:
     - a likely explanation for the contradiction
     - specific questions the patient should ask their doctor
     - urgency level: high medium or low
     
     format:
     INVESTIGATION REPORT
     [contradiction or gap]
     likely explanation: [your analysis]
     questions to ask: [specific questions]
     urgency: [high/medium/low]"""),
     # system message gives the llm its role and tells it exactly what format to use
    ("human", "conflicts and gaps to investigate:\n{conflicts}")])
    # {conflicts} gets filled with the output of the conflict agent
    # so the investigator reads what the conflict agent found and digs deeper

# connect prompt to llm
investigator_chain = investigator_prompt | llm

def investigator_agent(conflicts: str) -> str:# takes the conflicts string from the conflict agent as input
                                              # passes it to the llm and gets back a detailed investigation report
    print("investigator agent: digging deeper into conflicts found...")
    response = call_llm(investigator_chain, {"conflicts": conflicts})
    return response.content
    # returns a string with explanations questions and urgency levels
    # this gets passed to the reporter agent so it can include it in the final report


# test with fake conflicts to check the agent works alone
if __name__ == "__main__":
    test_conflicts = """
    bp was 145/90 in jan 2023 but 128/82 in june 2024 with no medication prescribed
    no eye exam recorded despite pre-diabetes since 2022
    """
    result = investigator_agent(test_conflicts)
    print(result)

#workflow:
#conflict agent finds: "bp jumped with no medication" then investigator reads it then 
#asks llm: why did this happen what should patient ask  returns: explanation + questions + urgency level
#reporter includes this in the final report