from typing import Dict, Any, List


def build_recommendation(
    completeness: Dict[str, Any],
    criteria_results: List[Dict[str, Any]],
    verification: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build a clinician-facing recommendation.

    Safety boundary:
    The coordinator can prepare a recommendation,
    but it cannot make the final clinical decision.
    """

    if not verification.get("verification_passed"):
        return {
            "recommendation": "Clinical review required",
            "rationale": "Verification failed. The case cannot advance automatically.",
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

    if not completeness.get("is_complete"):
        missing_documents = completeness.get("missing_documents", [])

        return {
            "recommendation": "More information required",
            "rationale": (
                "Required documentation is missing: "
                + ", ".join(missing_documents)
            ),
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

    not_demonstrated = [
        result
        for result in criteria_results
        if result.get("status") == "Not demonstrated"
    ]

    conflicting = [
        result
        for result in criteria_results
        if result.get("status") == "Conflicting"
    ]

    if conflicting:
        return {
            "recommendation": "Clinical review required",
            "rationale": "Conflicting clinical evidence was identified.",
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

    if not_demonstrated:
        criterion_ids = [
            result.get("criterion_id")
            for result in not_demonstrated
        ]

        return {
            "recommendation": "More information required",
            "rationale": (
                "Evidence was not demonstrated for criteria: "
                + ", ".join(criterion_ids)
            ),
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

    return {
        "recommendation": "Criteria appear met",
        "rationale": (
            "All required documentation is present, "
            "all evaluated criteria are supported by evidence, "
            "and independent verification passed."
        ),
        "human_review_required": True,
        "workflow_status": "HUMAN_REVIEW"
    }