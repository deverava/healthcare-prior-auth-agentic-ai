from typing import Dict, Any, List


def extract_evidence(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract structured evidence from clinical documents.

    For this first version, we use deterministic keyword-based extraction.
    Later, we will replace this logic with Claude.
    """

    extracted_evidence = []

    clinical_documents = case.get("clinical_documents", [])

    for document in clinical_documents:
        content = document.get("content", "").lower()

        evidence_item = {
            "document_id": document.get("document_id"),
            "document_type": document.get("document_type"),
            "document_date": document.get("document_date"),
            "findings": []
        }

        # MRI evidence
        if "acl tear" in content or "anterior cruciate ligament tear" in content:
            evidence_item["findings"].append({
                "fact": "ACL tear confirmed",
                "source_text": document.get("content"),
                "confidence": "high"
            })

        # Instability evidence
        if "instability" in content:
            evidence_item["findings"].append({
                "fact": "Knee instability documented",
                "source_text": document.get("content"),
                "confidence": "high"
            })

        # Physical therapy evidence
        if "physical therapy" in content:
            evidence_item["findings"].append({
                "fact": "Physical therapy attempted",
                "source_text": document.get("content"),
                "confidence": "high"
            })

        # Orthopedic recommendation
        if "acl reconstruction is recommended" in content:
            evidence_item["findings"].append({
                "fact": "ACL reconstruction recommended by orthopedic specialist",
                "source_text": document.get("content"),
                "confidence": "high"
            })

        if evidence_item["findings"]:
            extracted_evidence.append(evidence_item)

    return extracted_evidence