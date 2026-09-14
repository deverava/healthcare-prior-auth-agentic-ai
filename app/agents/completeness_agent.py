from typing import Any, Dict


def check_completeness(
    case: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generic policy-driven completeness check.

    The agent does not contain procedure-specific or
    disease-specific document mappings.

    Required documentation and acceptable document types
    come entirely from the selected policy.
    """

    required_documentation = policy.get(
        "required_documentation",
        [],
    )

    available_documents = case.get(
        "clinical_documents",
        [],
    )

    available_document_types = {
        document.get(
            "document_type",
            "",
        ).strip().lower()
        for document in available_documents
    }

    present_documents = []
    missing_documents = []
    requirement_results = []

    for requirement in required_documentation:

        # Backward compatibility:
        # support older policies where the requirement
        # may still be stored as a simple string.
        if isinstance(requirement, str):
            requirement_name = requirement

            accepted_document_types = [
                requirement
            ]

            requirement_id = None

        else:
            requirement_name = requirement.get(
                "name",
                "",
            )

            requirement_id = requirement.get(
                "requirement_id"
            )

            accepted_document_types = (
                requirement.get(
                    "accepted_document_types",
                    [],
                )
            )

        normalized_accepted_types = {
            document_type.strip().lower()
            for document_type
            in accepted_document_types
        }

        matched_document_types = sorted(
            available_document_types.intersection(
                normalized_accepted_types
            )
        )

        is_present = bool(
            matched_document_types
        )

        requirement_result = {
            "requirement_id": requirement_id,
            "name": requirement_name,
            "present": is_present,
            "matched_document_types":
                matched_document_types,
        }

        requirement_results.append(
            requirement_result
        )

        if is_present:
            present_documents.append(
                requirement_name
            )
        else:
            missing_documents.append(
                requirement_name
            )

    return {
        "is_complete":
            len(missing_documents) == 0,
        "present_documents":
            present_documents,
        "missing_documents":
            missing_documents,
        "requirement_results":
            requirement_results,
    }