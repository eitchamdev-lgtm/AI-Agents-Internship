# test_timeline.py
# this file tests that the timeline agent sorts dates corectly
# we pass data in the wrong order and check that 2022 comes before 2023 in the output
# this proves the sorting works and the agent didnt mix up the dates

from healthtrack.agents.timeline import timeline_agent

def test_timeline_sorts_by_date():
    # pass two reports in the wrong order (2023 first then 2022)
    # the timeline agent should sort them and put 2022 first
    unsorted_data = [
        {"clinic": "WellMed", "date": "2023-01-10",
         "doctor": "Dr. Jones", "findings": {"blood_pressure": "145/90"},
         "diagnosis": "pre-hypertension", "notes": "none"},
        {"clinic": "Chicago Clinic", "date": "2022-03-15",
         "doctor": "Dr. Smith", "findings": {"blood_pressure": "118/76"},
         "diagnosis": "healthy", "notes": "none"}
    ]

    result = timeline_agent(unsorted_data)

    # check that 2022 apears before 2023 in the output string
    # if the sorting is wrong 2023 would come first and this test would fail
    assert result.index("2022") < result.index("2023")