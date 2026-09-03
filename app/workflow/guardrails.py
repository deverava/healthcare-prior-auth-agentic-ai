from typing import Dict, Any


ADVERSE_DECISIONS = {
    "DENIED",
    "ADVERSE",
    "NOT_MEDICALLY_NECESSARY"
}


def validate_decision_request(
    decision: str,
    human_approved: bool,
    approval_token: str | None = None
) -> Dict[str, Any]:
    """
    Enforce safety rules before any decision service write.

    Adverse decisions require explicit human approval
    and an approval token.
    """

    normalized_decision = decision.strip().upper()

    if normalized_decision in ADVERSE_DECISIONS:
        if not human_approved:
            return {
                "allowed": False,
                "reason": (
                    "Adverse decision blocked. "
                    "Authorized human approval is required."
                )
            }

        if not approval_token:
            return {
                "allowed": False,
                "reason": (
                    "Adverse decision blocked. "
                    "Human approval token is missing."
                )
            }

    return {
        "allowed": True,
        "reason": "Decision request passed guardrail checks."
    }