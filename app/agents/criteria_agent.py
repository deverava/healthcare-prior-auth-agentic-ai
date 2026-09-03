from typing import Dict, Any, List


def evaluate_criteria(
    policy: Dict[str, Any],
    extracted_evidence: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Map policy criteria to extracted clinical evidence.

    Safety rule:
    Missing evidence is classified as "Not demonstrated",
    not automatically as "Not met".
    """

    criteria_results = []
    findings = []

    # Flatten evidence from all clinical documents
    for document in extracted_evidence:
        for finding in document.get("findings", []):
            findings.append({
                "fact": finding.get("fact", ""),
                "source_text": finding.get("source_text", ""),
                "confidence": finding.get("confidence", ""),
                "document_id": document.get("document_id"),
                "document_type": document.get("document_type")
            })

    # Evaluate each policy criterion
    for criterion in policy.get("criteria", []):
        criterion_id = criterion.get("criterion_id")
        description = criterion.get("description", "").lower()

        matched_evidence = []

        # Criterion 1 - ACL tear confirmed by imaging
        if "acl tear" in description or "diagnostic imaging" in description:
            matched_evidence = [
                item for item in findings
                if "acl tear confirmed" in item["fact"].lower()
            ]

        # Criterion 2 - Knee instability / functional limitation
        elif "instability" in description or "functional limitation" in description:
            matched_evidence = [
                item for item in findings
                if "instability documented" in item["fact"].lower()
            ]

        # Criterion 3 - Conservative treatment / physical therapy
        elif "conservative treatment" in description or "physical therapy" in description:
            matched_evidence = [
                item for item in findings
                if "physical therapy attempted" in item["fact"].lower()
            ]

        # Criterion 4 - Orthopedic recommendation
        elif "orthopedic specialist" in description:
            matched_evidence = [
                item for item in findings
                if "recommended by orthopedic specialist" in item["fact"].lower()
            ]

        status = "Met" if matched_evidence else "Not demonstrated"

        criteria_results.append({
            "criterion_id": criterion_id,
            "description": criterion.get("description"),
            "status": status,
            "evidence": matched_evidence
        })

    return criteria_results