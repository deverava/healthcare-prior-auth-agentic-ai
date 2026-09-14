from typing import Dict, Any, List


def evaluate_criteria(
    policy: Dict[str, Any],
    extracted_evidence: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    criteria_results = []

    for criterion in policy.get("criteria", []):

        criterion_id = criterion.get(
            "criterion_id"
        )

        positive_evidence = []
        negative_evidence = []

        for document in extracted_evidence:

            for evidence in document.get(
                "criterion_evidence",
                [],
            ):

                if (
                    evidence.get("criterion_id")
                    != criterion_id
                ):
                    continue

                evidence_record = {
                    "document_id": document.get(
                        "document_id"
                    ),
                    "document_type": document.get(
                        "document_type"
                    ),
                    "document_date": document.get(
                        "document_date"
                    ),
                    "source_text": evidence.get(
                        "source_text"
                    ),
                    "matched_terms": evidence.get(
                        "matched_terms",
                        [],
                    ),
                    "confidence": evidence.get(
                        "confidence"
                    ),
                }

                if (
                    evidence.get("evidence_type")
                    == "positive"
                ):

                    positive_evidence.append(
                        evidence_record
                    )

                elif (
                    evidence.get("evidence_type")
                    == "negative"
                ):

                    negative_evidence.append(
                        evidence_record
                    )

        if (
            positive_evidence
            and negative_evidence
        ):

            status = "Conflicting"

        elif positive_evidence:

            status = "Met"

        else:

            status = "Not demonstrated"

        criteria_results.append(
            {
                "criterion_id": criterion_id,
                "description": criterion.get(
                    "description"
                ),
                "status": status,
                "evidence": positive_evidence,
                "conflicting_evidence": (
                    negative_evidence
                ),
            }
        )

    return criteria_results