# test_plot.py
# this file tests the _systolic helper function in reporter.py
# _systolic safely extracts the first number from a bp string like 145/90
# we test it with all kinds of bad input to make sure it never crashes
# this is importent because if _systolic crashes the graph never renders

from healthtrack.agents.reporter import _systolic

def test_systolic_normal():
    # normal bp value should return just the first number
    assert _systolic("145/90") == 145

def test_systolic_none():
    # if bp is None it should return None not crash
    assert _systolic(None) is None

def test_systolic_junk():
    # if bp is a junk string it should return None not crash
    assert _systolic("bad_value") is None

def test_systolic_na():
    # if bp is the NA sentinel the llm sometimes returns it should return None not crash
    assert _systolic("NA") is None

def test_systolic_empty():
    # if bp is an empty string it should return None not crash
    assert _systolic("") is None