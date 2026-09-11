import json
from pathlib import Path

from app.workflow.graph import run_workflow


def load_wrong_policy_case():
    case_file = Path(
        "data/cases/wrong_policy_version.json"
    )

    with open(
        case_file,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_expired_policy_is_not_used():

    case = load_wrong_policy_case()

    state = run_workflow(case)

    # No valid policy should be selected for the 2027 request.
    assert state["policy"] is None

    assert "No matching policy was found." in state["errors"]

    assert (
        state["recommendation"]["recommendation"]
        == "Clinical review required"
    )

    assert state["current_stage"] == "HUMAN_REVIEW"

    assert state["human_review_required"] is True