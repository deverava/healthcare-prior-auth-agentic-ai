import json
from pathlib import Path

from app.workflow.graph import run_workflow


def load_case():
    case_file = Path("data/cases/conflicting_evidence.json")

    with open(case_file, "r", encoding="utf-8") as file:
        return json.load(file)


def test_conflicting_evidence_routes_to_human_review():

    case = load_case()

    state = run_workflow(case)

    criteria_results = state["criteria_matrix"]

    conflicting_results = [
        result
        for result in criteria_results
        if result["status"] == "Conflicting"
    ]

    assert len(conflicting_results) >= 1

    assert (
        state["recommendation"]["recommendation"]
        == "Clinical review required"
    )

    assert state["current_stage"] == "HUMAN_REVIEW"

    assert state["human_review_required"] is True