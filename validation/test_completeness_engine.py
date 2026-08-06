from engine.intelligence.v3.completeness_engine import calculate_completeness


def test_complete_profile():

    competencies = {
        "A": 75,
        "B": 72,
        "C": 68,
        "D": 70,
    }

    result = calculate_completeness(competencies)

    assert result.is_complete_candidate is True
    assert result.minimum == 68.0
    assert result.range == 7.0


def test_unbalanced_high_level_profile():

    competencies = {
        "A": 100,
        "B": 82,
        "C": 70,
        "D": 60,
    }

    result = calculate_completeness(competencies)

    assert result.is_complete_candidate is False
    assert result.range == 40.0


def test_balanced_but_low_level_profile():

    competencies = {
        "A": 58,
        "B": 57,
        "C": 55,
        "D": 56,
    }

    result = calculate_completeness(competencies)

    assert result.is_complete_candidate is False
