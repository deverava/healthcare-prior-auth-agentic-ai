from typing import Dict, Any

from app.services.policy_service import find_matching_policy
from app.services.audit_service import write_audit_event

from app.agents.evidence_agent import extract_evidence
from app.agents.completeness_agent import check_completeness
from app.agents.criteria_agent import evaluate_criteria
from app.agents.verifier_agent import verify_criteria_results
from app.agents.coordinator_agent import build_recommendation


def run_workflow(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Application-owned prior authorization workflow.

    The application controls workflow state and execution order.
    Agents perform bounded tasks but do not control the final
    clinical decision.
    """

    state = {
        "case": case,
        "current_stage": "INTAKE",
        "policy": None,
        "extracted_evidence": [],
        "completeness": {},
        "criteria_matrix": [],
        "verification": {},
        "recommendation": {},
        "human_review_required": True,
        "errors": []
    }

    case_id = case["case_id"]

    # ---------------------------------------------------------
    # STAGE 1: INTAKE
    # ---------------------------------------------------------
    write_audit_event(
        case_id=case_id,
        stage="INTAKE",
        event_type="WORKFLOW_STARTED",
        details={
            "procedure_code":
                case["requested_service"]["procedure_code"],
            "product_code":
                case["insurance"]["product_code"],
            "urgency":
                case["urgency"]
        }
    )

    # ---------------------------------------------------------
    # STAGE 2: POLICY RESOLUTION
    # ---------------------------------------------------------
    state["current_stage"] = "POLICY_RESOLUTION"

    policy = find_matching_policy(
        product_code=case["insurance"]["product_code"],
        procedure_code=case["requested_service"]["procedure_code"],
        request_date=case["request_date"]
    )

    if policy is None:
        state["errors"].append(
            "No matching policy was found."
        )

        state["recommendation"] = {
            "recommendation": "Clinical review required",
            "rationale":
                "A matching policy could not be resolved.",
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

        state["current_stage"] = "HUMAN_REVIEW"

        write_audit_event(
            case_id=case_id,
            stage="POLICY_RESOLUTION",
            event_type="POLICY_NOT_FOUND",
            details={
                "procedure_code":
                    case["requested_service"]["procedure_code"],
                "product_code":
                    case["insurance"]["product_code"]
            }
        )

        return state

    state["policy"] = policy

    write_audit_event(
        case_id=case_id,
        stage="POLICY_RESOLUTION",
        event_type="POLICY_SELECTED",
        details={
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"]
        }
    )

    # ---------------------------------------------------------
    # STAGE 3: EVIDENCE EXTRACTION
    # ---------------------------------------------------------
    state["current_stage"] = "EVIDENCE_EXTRACTION"

    evidence = extract_evidence(case)

    state["extracted_evidence"] = evidence

    write_audit_event(
        case_id=case_id,
        stage="EVIDENCE_EXTRACTION",
        event_type="EVIDENCE_EXTRACTED",
        details={
            "documents_with_evidence": len(evidence)
        }
    )

    # ---------------------------------------------------------
    # STAGE 4: COMPLETENESS CHECK
    # ---------------------------------------------------------
    state["current_stage"] = "COMPLETENESS_CHECK"

    completeness = check_completeness(
        case=case,
        policy=policy
    )

    state["completeness"] = completeness

    write_audit_event(
        case_id=case_id,
        stage="COMPLETENESS_CHECK",
        event_type="COMPLETENESS_EVALUATED",
        details={
            "is_complete": completeness["is_complete"],
            "missing_document_count":
                len(completeness["missing_documents"])
        }
    )

    # ---------------------------------------------------------
    # STAGE 5: CLINICAL CRITERIA
    # ---------------------------------------------------------
    state["current_stage"] = "CRITERIA_EVALUATION"

    criteria_results = evaluate_criteria(
        policy=policy,
        extracted_evidence=evidence
    )

    state["criteria_matrix"] = criteria_results

    criteria_summary = {
        result["criterion_id"]: result["status"]
        for result in criteria_results
    }

    write_audit_event(
        case_id=case_id,
        stage="CRITERIA_EVALUATION",
        event_type="CRITERIA_EVALUATED",
        details={
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"],
            "criteria_results": criteria_summary
        }
    )

    # ---------------------------------------------------------
    # STAGE 6: VERIFICATION
    # ---------------------------------------------------------
    state["current_stage"] = "VERIFICATION"

    verification = verify_criteria_results(
        criteria_results=criteria_results,
        policy=policy
    )

    state["verification"] = verification

    write_audit_event(
        case_id=case_id,
        stage="VERIFICATION",
        event_type="VERIFICATION_COMPLETED",
        details={
            "verification_passed":
                verification["verification_passed"],
            "issue_count":
                len(verification["issues"]),
            "policy_version":
                verification["policy_version"]
        }
    )

    # ---------------------------------------------------------
    # SAFETY STOP
    # ---------------------------------------------------------
    if not verification["verification_passed"]:
        state["recommendation"] = {
            "recommendation": "Clinical review required",
            "rationale":
                "Independent verification failed.",
            "human_review_required": True,
            "workflow_status": "HUMAN_REVIEW"
        }

        state["current_stage"] = "HUMAN_REVIEW"

        return state

    # ---------------------------------------------------------
    # STAGE 7: COORDINATOR
    # ---------------------------------------------------------
    state["current_stage"] = "COORDINATOR"

    recommendation = build_recommendation(
        completeness=completeness,
        criteria_results=criteria_results,
        verification=verification
    )

    state["recommendation"] = recommendation

    write_audit_event(
        case_id=case_id,
        stage="COORDINATOR",
        event_type="RECOMMENDATION_CREATED",
        details={
            "recommendation":
                recommendation["recommendation"],
            "human_review_required":
                recommendation["human_review_required"],
            "workflow_status":
                recommendation["workflow_status"]
        }
    )

    # ---------------------------------------------------------
    # STAGE 8: HUMAN REVIEW
    # ---------------------------------------------------------
    state["current_stage"] = "HUMAN_REVIEW"
    state["human_review_required"] = True

    write_audit_event(
        case_id=case_id,
        stage="HUMAN_REVIEW",
        event_type="HUMAN_REVIEW_REQUIRED",
        details={
            "recommendation":
                recommendation["recommendation"]
        }
    )

    return state