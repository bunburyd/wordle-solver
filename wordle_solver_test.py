
import pytest

import wordle_solver


expected_patterns = [
    ("raise", "point", "NNYNN"),
    ("blunt", "point", "NNNYY"),
    ("point", "point", "YYYYY"),
    ("goody", "cloud", "NNYSN"),
    ("spoon", "noops", "SSYSS")
]


@pytest.mark.parametrize("guess, answer, pattern", expected_patterns)
def test_wordle_compare(guess, answer, pattern):
    assert wordle_solver.wordle_compare(guess, answer) == pattern


def test_decision_tree():

    answers = ["goody", "raise", "plate", "point", "batch", "catch", "hatch"]

    decision_tree = wordle_solver.DecisionTree(answers, "latch")

    assert decision_tree.get_next_guess() == "latch"

    decision_tree.set_comparison("NYYYY")

    assert decision_tree.remaining_answers == ["batch", "catch", "hatch"]

    assert decision_tree.get_next_guess() == "batch"

    decision_tree.set_comparison("NYYYY")

    assert decision_tree.remaining_answers == ["catch", "hatch"]

    assert decision_tree.get_next_guess() == "catch"

    decision_tree.set_comparison("YYYYY")

    assert decision_tree.remaining_answers == ["catch"]



