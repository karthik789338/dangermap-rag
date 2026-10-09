import math

from score_correctness_v3 import (
    classify_fever,
    classify_pubmedqa,
    exact_match,
    numeric_match,
    score_correctness,
    token_f1,
)


assert exact_match(
    "The Eiffel Tower",
    "Eiffel Tower",
) == 1.0


assert math.isclose(
    token_f1(
        "West Lafayette Indiana",
        "West Lafayette, Indiana",
    ),
    1.0,
)


assert (
    classify_fever(
        "SUPPORTS"
    )
    == "SUPPORTS"
)

assert (
    classify_fever(
        "False"
    )
    == "REFUTES"
)


assert (
    classify_pubmedqa(
        "Yes, the study found..."
    )
    == "yes"
)

assert (
    classify_pubmedqa(
        "Maybe."
    )
    == "maybe"
)


assert numeric_match(
    "$1,250.50",
    "1250.5",
) == 1.0


assert numeric_match(
    "0.25",
    "25%",
) == 1.0


assert numeric_match(
    "The answer is 257",
    "257.0",
) == 1.0


x = score_correctness(
    "hotpotqa",
    "West Lafayette, Indiana",
    "West Lafayette Indiana",
)

assert math.isclose(
    x[
        "automated_correctness"
    ],
    1.0,
)


x = score_correctness(
    "fever",
    "REFUTES",
    "REFUTES",
)

assert (
    x[
        "automated_correctness"
    ]
    == 1.0
)


x = score_correctness(
    "pubmedqa",
    "Yes",
    "no",
)

assert (
    x[
        "automated_correctness"
    ]
    == 0.0
)


print(
    "CORRECTNESS UNIT TESTS: PASSED"
)

# A response mentioning the gold number only to reject it
# must not automatically receive full numeric correctness.
assert numeric_match(
    "257 is not the answer; the answer is 300",
    "257",
) != 1.0, (
    "Numeric evaluator is too permissive: "
    "matching any numeric mention can create false positives."
)
