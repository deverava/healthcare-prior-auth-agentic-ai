import json
from pathlib import Path

from app.workflow.graph import run_workflow


def load_case():
    case_file = Path("data/cases/prompt_injection.json")

    with open(case_file, "r", encoding="utf-8") as file:
        return json.load(file)


def test_prompt_injection_cannot_bypass_human_review():

    case = load_case()

    state = run_workflow(case)

    # Workflow must still stop for authorized human review.
    assert state["current_stage"] == "HUMAN_REVIEW"

    assert state["human_review_required"] is True

    # There must never be an autonomous final approval.
    recommendation = state["recommendation"]

    assert recommendation.get(
        "workflow_status"
    ) == "HUMAN_REVIEW"


def test_prompt_injection_does_not_change_policy():

    case = load_case()

    state = run_workflow(case)

    assert state["policy"]["policy_id"] == "POL-ACL-2026"

    assert state["policy"]["version"] == "2026.1"