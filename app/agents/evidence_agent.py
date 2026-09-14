import os
from typing import Any, Dict, List

from app.services.llm_service import (
    extract_clinical_evidence_with_llm,
)


def extract_evidence_deterministic(
    case: Dict[str, Any],
    policy: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Deterministic fallback evidence extractor.

    Uses evidence rules stored in the selected policy.
    """

    extracted_evidence = []
    criteria = policy.get("criteria", [])

    for document in case.get(
        "clinical_documents",
        [],
    ):
        content = document.get(
            "content",
            "",
        )

        content_lower = content.lower()

        document_type = document.get(
            "document_type",
            "",
        )

        document_evidence = {
            "document_id": document.get(
                "document_id"
            ),
            "document_type": document_type,
            "document_date": document.get(
                "document_date"
            ),
            "criterion_evidence": [],
        }

        for criterion in criteria:
            criterion_id = criterion.get(
                "criterion_id"
            )

            evidence_rule = criterion.get(
                "evidence_rule",
                {},
            )

            positive_terms = [
                term.lower()
                for term in evidence_rule.get(
                    "positive_terms",
                    [],
                )
            ]

            negative_terms = [
                term.lower()
                for term in evidence_rule.get(
                    "negative_terms",
                    [],
                )
            ]

            allowed_document_types = [
                value.lower()
                for value in evidence_rule.get(
                    "document_types",
                    [],
                )
            ]

            if allowed_document_types:
                if (
                    document_type.lower()
                    not in allowed_document_types
                ):
                    continue

            matched_positive = [
                term
                for term in positive_terms
                if term in content_lower
            ]

            matched_negative = [
                term
                for term in negative_terms
                if term in content_lower
            ]

            if matched_negative:
                document_evidence[
                    "criterion_evidence"
                ].append(
                    {
                        "criterion_id": criterion_id,
                        "evidence_type": "negative",
                        "matched_terms": matched_negative,
                        "source_text": content,
                        "confidence": "high",
                    }
                )

            elif matched_positive:
                document_evidence[
                    "criterion_evidence"
                ].append(
                    {
                        "criterion_id": criterion_id,
                        "evidence_type": "positive",
                        "matched_terms": matched_positive,
                        "source_text": content,
                        "confidence": "high",
                    }
                )

        if document_evidence[
            "criterion_evidence"
        ]:
            extracted_evidence.append(
                document_evidence
            )

    return extracted_evidence


def extract_evidence(
    case: Dict[str, Any],
    policy: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Main evidence extraction entry point.

    Uses OpenAI when AI_PROVIDER=openai.

    Falls back to deterministic extraction if the
    OpenAI request fails for any reason.
    """

    provider = os.getenv(
        "AI_PROVIDER",
        "deterministic",
    ).lower()

    if provider == "openai":
        try:
            return (
                extract_clinical_evidence_with_llm(
                    case=case,
                    policy=policy,
                )
            )

        except Exception as exc:
            print(
                "\nWARNING: OpenAI evidence extraction "
                "failed."
            )

            print(
                f"Reason: {exc}"
            )

            print(
                "Using deterministic evidence "
                "extraction fallback."
            )

    return extract_evidence_deterministic(
        case=case,
        policy=policy,
    )