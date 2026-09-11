from typing import Dict, Any, List


def evaluate_criteria(
    policy: Dict[str, Any],
    extracted_evidence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    criteria_results = []
    findings = []

    for document in extracted_evidence:

        for finding in document.get("findings", []):

            findings.append(
                {
                    "fact": finding.get("fact", ""),
                    "source_text": finding.get("source_text", ""),
                    "confidence": finding.get("confidence", ""),
                    "document_id": document.get("document_id"),
                    "document_type": document.get("document_type"),
                }
            )

    for criterion in policy.get("criteria", []):

        criterion_id = criterion.get("criterion_id")
        description = criterion.get(
            "description",
            "",
        ).lower()

        matched_evidence = []
        conflicting_evidence = []

        # ACL tear / imaging criterion
        if (
            "acl tear" in description
            or "diagnostic imaging" in description
        ):

            matched_evidence = [
                item
                for item in findings
                if "acl tear confirmed" in item["fact"].lower()
            ]

        # Instability / functional limitation criterion
        elif (
            "instability" in description
            or "functional limitation" in description
        ):

            positive_evidence = [
                item
                for item in findings
                if (
                    "knee instability documented"
                    in item["fact"].lower()
                )
            ]

            negative_evidence = [
                item
                for item in findings
                if (
                    "knee instability denied"
                    in item["fact"].lower()
                )
            ]

            if positive_evidence and negative_evidence:

                matched_evidence = positive_evidence
                conflicting_evidence = negative_evidence

            else:

                matched_evidence = positive_evidence

        # Conservative treatment criterion
        elif (
            "conservative treatment" in description
            or "physical therapy" in description
        ):

            matched_evidence = [
                item
                for item in findings
                if (
                    "physical therapy attempted"
                    in item["fact"].lower()
                )
            ]

        # Specialist recommendation criterion
        elif "orthopedic specialist" in description:

            matched_evidence = [
                item
                for item in findings
                if (
                    "recommended by orthopedic specialist"
                    in item["fact"].lower()
                )
            ]

        # Determine status
        if conflicting_evidence:

            status = "Conflicting"

        elif matched_evidence:

            status = "Met"

        else:

            status = "Not demonstrated"

        criteria_results.append(
            {
                "criterion_id": criterion_id,
                "description": criterion.get("description"),
                "status": status,
                "evidence": matched_evidence,
                "conflicting_evidence": conflicting_evidence,
            }
        )

    return criteria_results