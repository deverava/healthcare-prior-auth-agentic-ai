from datetime import datetime, timezone
from typing import Dict, Any

from app.workflow.guardrails import validate_decision_request


def submit_decision(
    case_id: str,
    decision: str,
    human_approved: bool,
    reviewer_id: str | None = None,
    approval_token: str | None = None
) -> Dict[str, Any]:
    """
    Mock system-of-record decision service.

    This does not connect to a real payer system.
    It demonstrates deterministic authorization controls.
    """

    guardrail_result = validate_decision_request(
        decision=decision,
        human_approved=human_approved,
        approval_token=approval_token
    )

    if not guardrail_result["allowed"]:
        return {
            "success": False,
            "case_id": case_id,
            "decision": decision,
            "message": guardrail_result["reason"]
        }

    return {
        "success": True,
        "case_id": case_id,
        "decision": decision.upper(),
        "reviewer_id": reviewer_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Mock decision recorded successfully."
    }