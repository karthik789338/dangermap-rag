import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(
    0,
    str(
        ROOT
        / "revision_v3"
        / "phase2"
        / "scripts"
    ),
)

from scoring_v3 import (
    DEFAULT_WEIGHTS,
    citation_unfaithful_silent_failure,
    danger_components,
    danger_score,
    normalize_expressed_confidence,
    silent_failure,
    validate_weights,
)


def test_reference_silent_failure():
    assert silent_failure(
        correctness=0.20,
        expressed_confidence=0.90,
        citation_appearance=0.80,
        abstained=False,
    )


def test_correct_answer_not_sf():
    assert not silent_failure(
        correctness=0.90,
        expressed_confidence=0.95,
        citation_appearance=0.90,
        abstained=False,
    )


def test_low_confidence_not_sf():
    assert not silent_failure(
        correctness=0.20,
        expressed_confidence=0.40,
        citation_appearance=0.90,
        abstained=False,
    )


def test_low_citation_appearance_not_sf():
    assert not silent_failure(
        correctness=0.20,
        expressed_confidence=0.90,
        citation_appearance=0.20,
        abstained=False,
    )


def test_abstention_never_sf():
    assert not silent_failure(
        correctness=None,
        expressed_confidence=None,
        citation_appearance=None,
        abstained=True,
    )


def test_abstention_score_zero():
    assert danger_score(
        correctness=None,
        expressed_confidence=None,
        citation_appearance=None,
        citation_faithfulness=None,
        abstained=True,
    ) == 0.0


def test_unfaithful_sf_subset():
    assert (
        citation_unfaithful_silent_failure(
            correctness=0.20,
            expressed_confidence=0.90,
            citation_appearance=0.90,
            citation_faithfulness=0.10,
            abstained=False,
        )
    )


def test_faithful_sf_not_in_unfaithful_subset():
    assert not (
        citation_unfaithful_silent_failure(
            correctness=0.20,
            expressed_confidence=0.90,
            citation_appearance=0.90,
            citation_faithfulness=0.90,
            abstained=False,
        )
    )


def test_no_citation_allows_missing_faithfulness():
    components = danger_components(
        correctness=0.30,
        expressed_confidence=0.80,
        citation_appearance=0.0,
        citation_faithfulness=None,
        abstained=False,
    )

    assert (
        components[
            "citation_misgrounding"
        ]
        == 0.0
    )


def test_present_citation_requires_faithfulness():
    try:
        danger_score(
            correctness=0.30,
            expressed_confidence=0.80,
            citation_appearance=0.80,
            citation_faithfulness=None,
            abstained=False,
        )

    except ValueError:
        return

    raise AssertionError(
        "Missing faithfulness should fail "
        "when citation appearance > 0"
    )


def test_equal_default_weights():
    assert math.isclose(
        sum(
            DEFAULT_WEIGHTS.values()
        ),
        1.0,
    )

    assert all(
        math.isclose(
            x,
            0.25,
        )
        for x in
        DEFAULT_WEIGHTS.values()
    )


def test_weight_validation():
    validate_weights({
        "incorrectness": 0.40,
        "expressed_confidence": 0.20,
        "citation_appearance": 0.20,
        "citation_misgrounding": 0.20,
    })


def test_invalid_weight_sum_fails():
    try:
        validate_weights({
            "incorrectness": 0.50,
            "expressed_confidence": 0.50,
            "citation_appearance": 0.50,
            "citation_misgrounding": 0.50,
        })

    except ValueError:
        return

    raise AssertionError(
        "Invalid weight sum accepted"
    )


def test_legacy_confidence_normalization():
    assert math.isclose(
        normalize_expressed_confidence(
            70
        ),
        0.70,
    )

    assert math.isclose(
        normalize_expressed_confidence(
            0.70
        ),
        0.70,
    )


def test_danger_score_expected_value():
    # I = .8
    # C = .9
    # V = .8
    # U = .8 * .9 = .72
    expected = (
        0.8
        + 0.9
        + 0.8
        + 0.72
    ) / 4.0

    observed = danger_score(
        correctness=0.20,
        expressed_confidence=0.90,
        citation_appearance=0.80,
        citation_faithfulness=0.10,
        abstained=False,
    )

    assert math.isclose(
        observed,
        expected,
        abs_tol=1e-12,
    )


def test_no_domain_multiplier():
    # Domain is deliberately absent from
    # the revised scoring interface.
    score = danger_score(
        correctness=0.20,
        expressed_confidence=0.90,
        citation_appearance=0.80,
        citation_faithfulness=0.10,
        abstained=False,
    )

    assert 0.0 <= score <= 1.0
