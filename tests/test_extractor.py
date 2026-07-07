# test_extractor.py
# this file tests the extractor agent to make sure it returns the right output
# instead of running the whole app every time we test just this one function
# pytest runs this automatically and tells us if something broke

from healthtrack.agents.extractor import extractor_agent

def test_extractor_returns_list():
    # simulate what the orchestrator passes to the extractor
    # a dict where key is the filename and value is the raw text content
    raw_texts = {
        "test_report.txt": """
        Chicago Clinic - Annual Checkup
        Date: 2022-03-15
        Doctor: Dr. Sarah Smith
        Blood Pressure: 118/76
        Glucose: 95
        Diagnosis: Healthy
        """
    }
    results = extractor_agent(raw_texts)

    # check that the output is a list
    assert isinstance(results, list)

    # check that we got one dict back for the one file we passed
    assert len(results) == 1

    # check that the dict has the keys we expect
    # source_file is always added by the extractor so we can track which file it came from
    result = results[0]
    assert "source_file" in result