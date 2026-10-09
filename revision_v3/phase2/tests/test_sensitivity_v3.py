import sys
from pathlib import Path

import numpy as np
import pandas as pd

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

from sensitivity_v3 import (
    REFERENCE,
    THRESHOLD_GRID,
    WEIGHT_REGIMES,
    jaccard_binary,
    sf_labels,
    threshold_sensitivity,
    weight_sensitivity,
)


def synthetic_df():
    rows = []

    for base in range(20):
        for condition in range(6):

            rows.append({
                "base_id":
                    f"b{base}",

                "model":
                    "synthetic",

                "dataset":
                    "test",

                "condition":
                    str(condition),

                "correctness":
                    ((base + condition) % 10)
                    / 10.0,

                "expressed_confidence":
                    (
                        0.55
                        + (
                            (base * 3 + condition)
                            % 40
                        ) / 100.0
                    ),

                "citation_appearance":
                    (
                        0.35
                        + (
                            (base + 2 * condition)
                            % 60
                        ) / 100.0
                    ),

                "citation_faithfulness":
                    (
                        (
                            base
                            + condition * 3
                        )
                        % 10
                    ) / 10.0,

                "abstained":
                    (
                        (base + condition)
                        % 13 == 0
                    ),
            })

    return pd.DataFrame(rows)


def test_grid_has_27_settings():
    assert len(
        THRESHOLD_GRID
    ) == 27


def test_reference_in_grid():
    ref = (
        REFERENCE["tau_A"],
        REFERENCE["tau_C"],
        REFERENCE["tau_V"],
    )

    assert ref in THRESHOLD_GRID


def test_four_weight_regimes():
    assert set(
        WEIGHT_REGIMES
    ) == {
        "equal",
        "incorrectness_heavy",
        "confidence_heavy",
        "citation_heavy",
    }


def test_all_weights_sum_one():
    for weights in (
        WEIGHT_REGIMES.values()
    ):
        assert np.isclose(
            sum(weights.values()),
            1.0,
        )


def test_jaccard_identity():
    x = [0, 1, 1, 0]

    assert (
        jaccard_binary(x, x)
        == 1.0
    )


def test_threshold_monotonicity_A():
    df = synthetic_df()

    low = sf_labels(
        df,
        tau_A=0.40,
        tau_C=0.70,
        tau_V=0.50,
    )

    high = sf_labels(
        df,
        tau_A=0.60,
        tau_C=0.70,
        tau_V=0.50,
    )

    # Increasing tau_A makes the
    # incorrectness criterion less strict.
    assert high.sum() >= low.sum()


def test_threshold_monotonicity_C():
    df = synthetic_df()

    low = sf_labels(
        df,
        tau_A=0.50,
        tau_C=0.60,
        tau_V=0.50,
    )

    high = sf_labels(
        df,
        tau_A=0.50,
        tau_C=0.80,
        tau_V=0.50,
    )

    assert high.sum() <= low.sum()


def test_threshold_monotonicity_V():
    df = synthetic_df()

    low = sf_labels(
        df,
        tau_A=0.50,
        tau_C=0.70,
        tau_V=0.40,
    )

    high = sf_labels(
        df,
        tau_A=0.50,
        tau_C=0.70,
        tau_V=0.60,
    )

    assert high.sum() <= low.sum()


def test_threshold_analysis_has_reference():
    df = synthetic_df()

    out = threshold_sensitivity(
        df,
        bootstrap_iterations=50,
    )

    assert len(out) == 27
    assert out[
        "is_reference"
    ].sum() == 1

    ref = out[
        out["is_reference"]
    ].iloc[0]

    assert np.isclose(
        ref[
            "absolute_rate_change"
        ],
        0.0,
    )

    assert np.isclose(
        ref[
            "jaccard_vs_reference"
        ],
        1.0,
    )


def test_weight_analysis():
    df = synthetic_df()

    out = weight_sensitivity(
        df
    )

    assert len(out) == 4

    equal = out[
        out["weight_regime"]
        == "equal"
    ].iloc[0]

    assert np.isclose(
        equal[
            "spearman_vs_equal"
        ],
        1.0,
    )

    assert np.isclose(
        equal[
            "top_decile_jaccard"
        ],
        1.0,
    )

    assert np.isclose(
        equal[
            "mean_absolute_score_change"
        ],
        0.0,
    )
