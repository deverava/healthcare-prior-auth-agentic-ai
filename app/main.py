import json
from pathlib import Path

from app.models.case import PriorAuthorizationCase
from app.workflow.graph import run_workflow


def load_case(case_name: str = "happy_path") -> PriorAuthorizationCase:
    """
    Load a synthetic prior authorization case.
    """

    case_file = Path(f"data/cases/{case_name}.json")

    with open(case_file, "r", encoding="utf-8") as file:
        case_data = json.load(file)

    return PriorAuthorizationCase(**case_data)


def main():
    # ---------------------------------------------------------
    # 1. LOAD CASE
    # ---------------------------------------------------------
    case = load_case("happy_path")

    print("\n==========================================")
    print("Healthcare Prior Authorization POC")
    print("==========================================")

    print(f"\nCase ID: {case.case_id}")
    print(f"Procedure: {case.requested_service.procedure_name}")
    print(f"Procedure Code: {case.requested_service.procedure_code}")
    print(f"Product Code: {case.insurance.product_code}")
    print(f"Urgency: {case.urgency}")

    print("\nStarting Agentic Workflow...")

    # ---------------------------------------------------------
    # 2. RUN APPLICATION STATE MACHINE
    # ---------------------------------------------------------
    state = run_workflow(case.model_dump())

    # ---------------------------------------------------------
    # 3. DISPLAY POLICY
    # ---------------------------------------------------------
    policy = state.get("policy")

    print("\n------------------------------------------")
    print("Policy Resolution")
    print("------------------------------------------")

    if policy:
        print(f"Policy ID: {policy['policy_id']}")
        print(f"Policy Name: {policy['policy_name']}")
        print(f"Version: {policy['version']}")
    else:
        print("No matching policy found.")

    # ---------------------------------------------------------
    # 4. DISPLAY EVIDENCE
    # ---------------------------------------------------------
    print("\n------------------------------------------")
    print("Evidence Agent")
    print("------------------------------------------")

    extracted_evidence = state.get(
        "extracted_evidence",
        []
    )

    if extracted_evidence:
        for document in extracted_evidence:
            print(
                f"\nDocument: "
                f"{document.get('document_type')}"
            )

            print(
                f"Document ID: "
                f"{document.get('document_id')}"
            )

            criterion_evidence = document.get(
                "criterion_evidence",
                []
            )

            for evidence in criterion_evidence:
                criterion_id = evidence.get(
                    "criterion_id"
                )

                evidence_type = evidence.get(
                    "evidence_type"
                )

                matched_terms = evidence.get(
                    "matched_terms",
                    []
                )

                print(
                    f"  - Criterion: {criterion_id}"
                )

                print(
                    f"    Evidence Type: "
                    f"{evidence_type}"
                )

                if matched_terms:
                    print(
                        "    Matched Terms: "
                        + ", ".join(matched_terms)
                    )

    else:
        print("No relevant evidence extracted.")

    # ---------------------------------------------------------
    # 5. DISPLAY COMPLETENESS
    # ---------------------------------------------------------
    print("\n------------------------------------------")
    print("Completeness Agent")
    print("------------------------------------------")

    completeness = state.get("completeness", {})

    if completeness:
        print(
            f"Case Complete: "
            f"{completeness.get('is_complete')}"
        )

        missing = completeness.get(
            "missing_documents",
            []
        )

        if missing:
            print("Missing Documentation:")

            for document in missing:
                print(f"  - {document}")

        else:
            print("Missing Documentation: None")

    # ---------------------------------------------------------
    # 6. DISPLAY CRITERIA
    # ---------------------------------------------------------
    print("\n------------------------------------------")
    print("Clinical Criteria Agent")
    print("------------------------------------------")

    criteria = state.get(
        "criteria_matrix",
        []
    )

    for result in criteria:
        print(
            f"{result.get('criterion_id')} -> "
            f"{result.get('status')}"
        )

        evidence_items = result.get(
            "evidence",
            []
        )

        for item in evidence_items:
            print(
                f"    Evidence: "
                f"{item.get('document_type')} "
                f"({item.get('document_id')})"
            )

        conflicting_items = result.get(
            "conflicting_evidence",
            []
        )

        for item in conflicting_items:
            print(
                f"    Conflicting Evidence: "
                f"{item.get('document_type')} "
                f"({item.get('document_id')})"
            )

    # ---------------------------------------------------------
    # 7. DISPLAY VERIFICATION
    # ---------------------------------------------------------
    print("\n------------------------------------------")
    print("Verifier Agent")
    print("------------------------------------------")

    verification = state.get(
        "verification",
        {}
    )

    if verification:
        print(
            f"Verification Passed: "
            f"{verification.get('verification_passed')}"
        )

        issues = verification.get(
            "issues",
            []
        )

        if issues:
            print("Issues:")

            for issue in issues:
                print(f"  - {issue}")

        else:
            print("Verification Issues: None")

    # ---------------------------------------------------------
    # 8. DISPLAY COORDINATOR RESULT
    # ---------------------------------------------------------
    print("\n------------------------------------------")
    print("Coordinator Agent")
    print("------------------------------------------")

    recommendation = state.get(
        "recommendation",
        {}
    )

    print(
        f"Recommendation: "
        f"{recommendation.get('recommendation')}"
    )

    print(
        f"Rationale: "
        f"{recommendation.get('rationale')}"
    )

    print(
        f"Human Review Required: "
        f"{recommendation.get('human_review_required')}"
    )

    # ---------------------------------------------------------
    # 9. FINAL WORKFLOW STATE
    # ---------------------------------------------------------
    print("\n==========================================")
    print("Workflow Result")
    print("==========================================")

    print(
        f"Current Stage: "
        f"{state.get('current_stage')}"
    )

    print(
        f"Human Review Required: "
        f"{state.get('human_review_required')}"
    )

    errors = state.get(
        "errors",
        []
    )

    if errors:
        print("\nWorkflow Errors:")

        for error in errors:
            print(f"  - {error}")

    print(
        "\nIMPORTANT: The AI workflow prepares "
        "decision-support information only."
    )

    print(
        "The final clinical decision remains "
        "with an authorized human reviewer."
    )


if __name__ == "__main__":
    main()