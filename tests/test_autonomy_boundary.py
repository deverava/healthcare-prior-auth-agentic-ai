from app.services.decision_service import submit_decision


def test_ai_cannot_deny_without_human_approval():
    result = submit_decision(
        case_id="PA-ACL-1001",
        decision="DENIED",
        human_approved=False
    )

    assert result["success"] is False


def test_denial_requires_approval_token():
    result = submit_decision(
        case_id="PA-ACL-1001",
        decision="DENIED",
        human_approved=True,
        reviewer_id="CLINICIAN-001",
        approval_token=None
    )

    assert result["success"] is False


def test_human_approved_decision_allowed():
    result = submit_decision(
        case_id="PA-ACL-1001",
        decision="DENIED",
        human_approved=True,
        reviewer_id="CLINICIAN-001",
        approval_token="HUMAN-APPROVAL-123"
    )

    assert result["success"] is True