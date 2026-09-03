from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class WorkflowState(TypedDict, total=False):

    # Original prior authorization case
    case: Dict[str, Any]

    # Policy selected for the case
    policy: Dict[str, Any]

    # Evidence extracted from clinical documents
    extracted_evidence: List[Dict[str, Any]]

    # Missing documentation identified by the workflow
    missing_evidence: List[str]

    # Mapping of policy criteria to clinical evidence
    criteria_matrix: List[Dict[str, Any]]

    # Independent verification results
    verification: Dict[str, Any]

    # AI-generated recommendation
    recommendation: Optional[str]

    # Explanation shown to clinician
    rationale: Optional[str]

    # Current workflow stage
    current_stage: str

    # Whether human review is required
    human_review_required: bool

    # Errors captured during workflow execution
    errors: List[str]