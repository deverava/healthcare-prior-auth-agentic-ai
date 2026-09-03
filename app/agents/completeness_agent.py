from typing import Dict, Any, List


DOCUMENT_TYPE_MAPPING = {
    "diagnostic imaging report": ["mri report", "ct report", "imaging report"],
    "orthopedic consultation note": ["orthopedic consultation"],
    "conservative treatment or physical therapy documentation": [
        "physical therapy record",
        "physical therapy",
        "conservative treatment"
    ]
}


def check_completeness(
    case: Dict[str, Any],
    policy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare required policy documentation against documents
    available in the prior authorization case.
    """

    required_documents = policy.get("required_documentation", [])
    clinical_documents = case.get("clinical_documents", [])

    available_document_types = [
        document.get("document_type", "").lower()
        for document in clinical_documents
    ]

    present_documents: List[str] = []
    missing_documents: List[str] = []

    for required_document in required_documents:
        required_key = required_document.lower()

        acceptable_types = DOCUMENT_TYPE_MAPPING.get(
            required_key,
            [required_key]
        )

        found = any(
            acceptable_type in available_document_type
            for acceptable_type in acceptable_types
            for available_document_type in available_document_types
        )

        if found:
            present_documents.append(required_document)
        else:
            missing_documents.append(required_document)

    return {
        "is_complete": len(missing_documents) == 0,
        "present_documents": present_documents,
        "missing_documents": missing_documents
    }