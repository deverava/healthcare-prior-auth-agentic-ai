import json
from pathlib import Path

from app.workflow.graph import run_workflow


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_lumbar_mri_uses_correct_policy():

    case_file = (
        PROJECT_ROOT
        / "data"
        / "cases"
        / "lumbar_mri.json"
    )

    with open(
        case_file,
        "r",
        encoding="utf-8",
    ) as file:
        case = json.load(file)

    state = run_workflow(case)

    policy = state.get("policy", {})

    assert policy.get("policy_id") == "POL-LMRI-2026"

    assert policy.get("version") == "2026.1"

    assert state.get("human_review_required") is True