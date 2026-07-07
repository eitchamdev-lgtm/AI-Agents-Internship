from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from healthtrack.config import GROQ_API_KEY, LLM_MODEL
from healthtrack.utils import call_llm

llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL)

# critic agent: runs after the reporter writes the summary   job: check if the report is good enough
# if not send it back to reporter once with notes on what to fix
# capped at 1 retry so it never loops forever this is the self correcting loop  the system improves its own output

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", """you are a medical report critic
     your job is to review a health summary report and check if it is good enough
     
     a good report must have:
     - a clear overview of the patients health journey
     - all key findings mentioned with actual numbers
     - all concerns and contradictions addressed
     - clear action items the patient can act on
     
     if the report is good respond with exactly: APPROVED
     if the report needs improvement respond with: NEEDS_REVISION
     then list specifically what is missing or unclear
     be concise and specific"""),
    ("human", "review this health report:\n{report}")])

critic_chain = critic_prompt | llm

def critic_agent(report: str) -> dict:
    # take the report from the reporter agent return a dict with two keys:
    # approved: true if report is good False if needs revision
    # feedback: the critics notes on what to fix (empty if approved)
    print("critic agent: reviewing the report...")
    response = call_llm(critic_chain, {"report": report})
    content = response.content.strip()

    if content.startswith("APPROVED"):
        print("critic: report approved")
        return {"approved": True, "feedback": ""}
    else:
        print("critic: report needs revision sending back to reporter")
        # extract the feedback after NEEDS_REVISION
        feedback = content.replace("NEEDS_REVISION", "").strip()
        return {"approved": False, "feedback": feedback}


if __name__ == "__main__":
    test_report = "the patient is doing ok and should see a doctor"
    result = critic_agent(test_report)
    print(result)