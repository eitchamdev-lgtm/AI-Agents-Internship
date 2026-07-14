# test_timeline.py
# this file tests that the timeline agent sorts dates corectly
# we pass data in the wrong order and check that 2022 comes before 2023 in the output
# this proves the sorting works and the agent didnt mix up the dates
import pytest
import os
from healthtrack.agents.timeline import sort_by_date #insted of importing timline_agent it tries to connect groq so now 
                                                     #we import sort by date where is function is pure py without api 
                                                     #so the pytest dosent crashes 

def test_timeline_sorts_by_date():
    # pass two reports in the wrong order (2023 first then 2022)
    # the timeline agent should sort them and put 2022 first
    unsorted_data = [{"clinic": "WellMed", "date": "2023-01-10",
         "doctor": "Dr. Jones", "findings": {"blood_pressure": "145/90"},
         "diagnosis": "pre-hypertension", "notes": "none"},
        {"clinic": "Chicago Clinic", "date": "2022-03-15",
         "doctor": "Dr. Smith", "findings": {"blood_pressure": "118/76"},
         "diagnosis": "healthy", "notes": "none"}]
    result = sort_by_date(unsorted_data)

    # check the first item is 2022 and second is 2023
    assert result[0]["date"] == "2022-03-15"
    assert result[1]["date"] == "2023-01-10"


# this test calls groq live so it needs an api key
# skipif means: if no api key in environment skip this test dont fail it
# on a fresh machine with no env file this test is skipped and pytest still passes green
@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="no api key skipping live llm test")
def test_timeline_agent_live():
    from healthtrack.agents.timeline import timeline_agent
    unsorted_data = [
        {"clinic": "WellMed", "date": "2023-01-10", "doctor": "Dr. Jones",
         "findings": {"blood_pressure": "145/90"}, "diagnosis": "pre-hypertension", "notes": "none"},
        {"clinic": "Chicago Clinic", "date": "2022-03-15", "doctor": "Dr. Smith",
         "findings": {"blood_pressure": "118/76"}, "diagnosis": "healthy", "notes": "none"}]
    result = timeline_agent(unsorted_data)
    assert "2022" in result
    assert "2023" in result

