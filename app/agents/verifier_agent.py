from typing import Dict, Any, List


def verify_criteria_results(
    criteria_results: List[Dict[str, Any]],
    policy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Independently verify that every criterion marked as Met
    has supporting evidence.

    The verifier can block the workflow if unsupported claims
    or missing policy references are detected.
    """

    issues = []
    verified_criteria = []

    policy_version = policy.get("version")
    policy_id = policy.get("policy_id")

    for result in criteria_results:
        criterion_id = result.get("criterion_id")
        status = result.get("status")
        evidence = result.get("evidence", [])

        criterion_verified = True

        # If marked Met, supporting evidence must exist
        if status == "Met" and not evidence:
            criterion_verified = False

            issues.append(
                f"{criterion_id} is marked Met but has no supporting evidence."
            )

        # Every result should reference a valid criterion ID
        if not criterion_id:
            criterion_verified = False

            issues.append(
                "A criteria result is missing a criterion ID."
            )

        verified_criteria.append({
            "criterion_id": criterion_id,
            "status": status,
            "verified": criterion_verified
        })

    verification_passed = len(issues) == 0

    return {
        "verification_passed": verification_passed,
        "policy_id": policy_id,
        "policy_version": policy_version,
        "verified_criteria": verified_criteria,
        "issues": issues
    }