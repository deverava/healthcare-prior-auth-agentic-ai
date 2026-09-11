from typing import Dict, Any, List


def extract_evidence(case: Dict[str, Any]) -> List[Dict[str, Any]]:

    extracted_evidence = []

    for document in case.get("clinical_documents", []):

        content = document.get("content", "")
        content_lower = content.lower()

        evidence_item = {
            "document_id": document.get("document_id"),
            "document_type": document.get("document_type"),
            "document_date": document.get("document_date"),
            "findings": [],
        }

        # ACL tear evidence
        if (
            "acl tear" in content_lower
            or "anterior cruciate ligament tear" in content_lower
        ):
            evidence_item["findings"].append(
                {
                    "fact": "ACL tear confirmed",
                    "source_text": content,
                    "confidence": "high",
                }
            )

        # Detect explicit negative instability statements first
        instability_denied = (
            "denies knee instability" in content_lower
            or "denies instability" in content_lower
            or "no knee instability" in content_lower
            or "no instability" in content_lower
        )

        if instability_denied:
            evidence_item["findings"].append(
                {
                    "fact": "Knee instability denied",
                    "source_text": content,
                    "confidence": "high",
                }
            )

        elif "instability" in content_lower:
            evidence_item["findings"].append(
                {
                    "fact": "Knee instability documented",
                    "source_text": content,
                    "confidence": "high",
                }
            )

        # Physical therapy evidence
        if "physical therapy" in content_lower:
            evidence_item["findings"].append(
                {
                    "fact": "Physical therapy attempted",
                    "source_text": content,
                    "confidence": "high",
                }
            )

        # Orthopedic recommendation
        if "acl reconstruction is recommended" in content_lower:
            evidence_item["findings"].append(
                {
                    "fact": (
                        "ACL reconstruction recommended "
                        "by orthopedic specialist"
                    ),
                    "source_text": content,
                    "confidence": "high",
                }
            )

        if evidence_item["findings"]:
            extracted_evidence.append(evidence_item)

    return extracted_evidence