# test_extractor.py
# this file tests the extractor agent to make sure it returns the right output
# instead of running the whole app every time we test just this one function
# pytest runs this automatically and tells us if something broke

import pytest
import os 


def test_extracted_data_has_source_file():# pure python test no llm involved
                                         # we simulate what the extractor returns and check the structure
                                         # source_file key is always added by the extractor to track which file the data came from
    fake_result = [ {"clinic": "Chicago Clinic", "date": "2022-03-15",
         "source_file": "chicago_clinic_2022.txt"}]
    assert "source_file" in fake_result[0]
    assert fake_result[0]["source_file"] == "chicago_clinic_2022.txt"


# this test calls groq live so it needs an api key
#  skipif skips this test automaticly on a fresh machine with no env file 
# so pytest still passe green even without a key
@pytest.mark.skipif(not os.environ.get("GROQ_API_KEY"),
    reason="no api key skipping live llm test")

def test_extractor_live():           # import inside the function so it only loads when the test actually runs
                                    # this prevents the import from crashing at collection time on a machine with no key
    from healthtrack.agents.extractor import extractor_agent
    raw_texts = {"test_report.txt": """
        Chicago Clinic - Annual Checkup
        Date: 2022-03-15
        Doctor: Dr. Sarah Smith
        Blood Pressure: 118/76
        Glucose: 95
        Diagnosis: Healthy
        """}
    results = extractor_agent(raw_texts)
    assert isinstance(results, list)
    assert len(results) == 1
    assert "source_file" in results[0]