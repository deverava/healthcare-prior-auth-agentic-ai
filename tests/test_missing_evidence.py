import json
from pathlib import Path

from app.workflow.graph import run_workflow


def load_case():
    case_file = Path("data/cases/missing_evidence.json")

    with open(case_file, "r", encoding="utf-8") as file:
        return json.load(file)


def test_missing_evidence_routes_to_human_review():

    case = load_case()

    state = run_workflow(case)

    assert state["completeness"]["is_complete"] is False

    assert (
        "Conservative treatment or physical therapy documentation"
        in state["completeness"]["missing_documents"]
    )

    acl_003 = next(
        result
        for result in state["criteria_matrix"]
        if result["criterion_id"] == "ACL-003"
    )

    assert acl_003["status"] == "Not demonstrated"

    assert (
        state["recommendation"]["recommendation"]
        == "More information required"
    )

    assert state["current_stage"] == "HUMAN_REVIEW"

    assert state["human_review_required"] is True