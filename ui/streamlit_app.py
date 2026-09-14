import sys
import json
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.workflow.graph import run_workflow
from app.services.decision_service import submit_decision


CASE_FOLDER = PROJECT_ROOT / "data" / "cases"


st.set_page_config(
    page_title="Prior Authorization Reviewer",
    page_icon="🏥",
    layout="wide",
)


def load_case(file_name: str):
    file_path = CASE_FOLDER / file_name

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def display_status(status: str):
    if status == "Met":
        st.success("Met")
    elif status == "Conflicting":
        st.warning("Conflicting")
    elif status == "Not demonstrated":
        st.info("Not demonstrated")
    else:
        st.write(status)


st.title("Healthcare Prior Authorization Reviewer")

st.caption(
    "AI-assisted clinical decision support with mandatory human review."
)


# --------------------------------------------------
# CASE SELECTION
# --------------------------------------------------

case_files = sorted(
    file.name
    for file in CASE_FOLDER.glob("*.json")
)


selected_case_file = st.sidebar.selectbox(
    "Select Prior Authorization Case",
    case_files,
)


if st.sidebar.button(
    "Run Prior Authorization Review",
    type="primary",
):
    case = load_case(
        selected_case_file
    )

    with st.spinner(
        "Running prior authorization workflow..."
    ):
        state = run_workflow(case)

    st.session_state["case"] = case
    st.session_state["state"] = state


# --------------------------------------------------
# DISPLAY WORKFLOW RESULT
# --------------------------------------------------

if (
    "case" in st.session_state
    and "state" in st.session_state
):

    case = st.session_state["case"]
    state = st.session_state["state"]

    case_id = case.get("case_id")

    # --------------------------------------------------
    # CASE SUMMARY
    # --------------------------------------------------

    st.header("Case Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Case ID",
            case_id,
        )

    with col2:
        st.metric(
            "Urgency",
            case.get(
                "urgency",
                "Unknown",
            ).title(),
        )

    with col3:
        st.metric(
            "Procedure Code",
            case.get(
                "requested_service",
                {},
            ).get(
                "procedure_code",
                "N/A",
            ),
        )

    with col4:
        st.metric(
            "Product Code",
            case.get(
                "insurance",
                {},
            ).get(
                "product_code",
                "N/A",
            ),
        )


    left, right = st.columns(2)

    with left:

        st.subheader("Requested Service")

        requested_service = case.get(
            "requested_service",
            {},
        )

        st.write(
            "**Procedure:**",
            requested_service.get(
                "procedure_name",
                "N/A",
            ),
        )

        st.write(
            "**Diagnosis:**",
            requested_service.get(
                "diagnosis",
                "N/A",
            ),
        )

        st.write(
            "**Diagnosis Code:**",
            requested_service.get(
                "diagnosis_code",
                "N/A",
            ),
        )

        st.write(
            "**Body Site:**",
            requested_service.get(
                "body_site",
                "N/A",
            ),
        )


    with right:

        st.subheader("Insurance")

        insurance = case.get(
            "insurance",
            {},
        )

        st.write(
            "**Payer:**",
            insurance.get(
                "payer",
                "N/A",
            ),
        )

        st.write(
            "**Plan:**",
            insurance.get(
                "plan_name",
                "N/A",
            ),
        )

        st.write(
            "**Product Code:**",
            insurance.get(
                "product_code",
                "N/A",
            ),
        )


    st.divider()


    # --------------------------------------------------
    # POLICY
    # --------------------------------------------------

    st.header("Selected Policy")

    policy = state.get(
        "policy",
        {},
    )

    if policy:

        policy_col1, policy_col2, policy_col3 = (
            st.columns(3)
        )

        with policy_col1:
            st.write(
                "**Policy:**",
                policy.get(
                    "policy_name",
                    "N/A",
                ),
            )

        with policy_col2:
            st.write(
                "**Version:**",
                policy.get(
                    "version",
                    "N/A",
                ),
            )

        with policy_col3:
            st.write(
                "**Policy ID:**",
                policy.get(
                    "policy_id",
                    "N/A",
                ),
            )

        st.write(
            "**Effective Period:**",
            f"{policy.get('effective_date', 'N/A')} "
            f"to "
            f"{policy.get('expiration_date', 'N/A')}",
        )

    else:
        st.error(
            "No valid policy was resolved "
            "for this request."
        )


    st.divider()


    # --------------------------------------------------
    # COMPLETENESS
    # --------------------------------------------------

    st.header("Documentation Completeness")

    missing_documents = state.get(
        "missing_evidence",
        [],
    )

    if not missing_documents:
        st.success(
            "Required documentation is complete."
        )
    else:
        st.warning(
            "Additional documentation is required."
        )

        for missing_document in missing_documents:
            st.write(
                f"- {missing_document}"
            )


    st.divider()


    # --------------------------------------------------
    # CRITERIA
    # --------------------------------------------------

    st.header("Clinical Criteria Review")

    criteria_results = state.get(
        "criteria_matrix",
        [],
    )

    if criteria_results:

        for result in criteria_results:

            criterion_id = result.get(
                "criterion_id",
                "Unknown",
            )

            description = result.get(
                "description",
                "",
            )

            status = result.get(
                "status",
                "Unknown",
            )

            with st.expander(
                f"{criterion_id} — {status}",
                expanded=True,
            ):

                st.write(description)

                display_status(status)

                evidence = result.get(
                    "evidence",
                    [],
                )

                conflicting_evidence = result.get(
                    "conflicting_evidence",
                    [],
                )

                if evidence:

                    st.markdown(
                        "**Supporting Evidence**"
                    )

                    for item in evidence:

                        st.write(
                            f"**{item.get('document_type')}** "
                            f"({item.get('document_id')})"
                        )

                        source_text = item.get(
                            "source_text"
                        )

                        if source_text:
                            st.info(
                                source_text
                            )

                        confidence = item.get(
                            "confidence"
                        )

                        if confidence:
                            st.caption(
                                f"Confidence: "
                                f"{confidence}"
                            )


                if conflicting_evidence:

                    st.markdown(
                        "**Conflicting Evidence**"
                    )

                    for item in conflicting_evidence:

                        st.warning(
                            item.get(
                                "source_text",
                                "Conflicting evidence detected.",
                            )
                        )

    else:
        st.info(
            "No clinical criteria results available."
        )


    st.divider()


    # --------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------

    st.header("Independent Verification")

    verification = state.get(
        "verification",
        {},
    )

    if verification.get(
        "verification_passed"
    ):
        st.success(
            "Verification Passed"
        )
    else:
        st.warning(
            "Verification requires review."
        )

        for issue in verification.get(
            "issues",
            [],
        ):
            st.write(
                f"- {issue}"
            )


    st.divider()


    # --------------------------------------------------
    # AI RECOMMENDATION
    # --------------------------------------------------

    st.header("AI Decision-Support Recommendation")

    recommendation = state.get(
        "recommendation"
    )

    rationale = state.get(
        "rationale"
    )

    if recommendation:

        if recommendation == "Criteria appear met":
            st.success(
                recommendation
            )

        elif recommendation == "More information required":
            st.warning(
                recommendation
            )

        else:
            st.info(
                recommendation
            )

        if rationale:
            st.write(
                "**Rationale:**",
                rationale,
            )

    else:
        st.info(
            "No recommendation available."
        )


    # --------------------------------------------------
    # HUMAN REVIEW
    # --------------------------------------------------

    st.divider()

    st.header("Human Clinical Review")

    st.warning(
        "Human Review Required — "
        "The AI system does not make the final "
        "prior authorization decision."
    )


    reviewer_id = st.text_input(
        "Reviewer ID",
        placeholder="Example: CLINICIAN-001",
    )


    human_confirmation = st.checkbox(
        "I confirm that I am the authorized "
        "human reviewer for this case."
    )


    st.subheader(
        "Reviewer Action"
    )


    action_col1, action_col2, action_col3 = (
        st.columns(3)
    )


    # --------------------------------------------------
    # APPROVE
    # --------------------------------------------------

    with action_col1:

        if st.button(
            "Approve",
            use_container_width=True,
        ):

            if not reviewer_id:
                st.error(
                    "Reviewer ID is required."
                )

            elif not human_confirmation:
                st.error(
                    "Human reviewer confirmation "
                    "is required."
                )

            else:

                result = submit_decision(
                    case_id=case_id,
                    decision="APPROVED",
                    human_approved=True,
                    reviewer_id=reviewer_id,
                    approval_token=(
                        f"HUMAN-{reviewer_id}"
                    ),
                )

                if result.get("success"):
                    st.success(
                        "Human approval recorded."
                    )
                else:
                    st.error(
                        result.get(
                            "reason",
                            "Decision could not be recorded.",
                        )
                    )


    # --------------------------------------------------
    # REQUEST MORE INFORMATION
    # --------------------------------------------------

    with action_col2:

        if st.button(
            "Request More Information",
            use_container_width=True,
        ):

            if not reviewer_id:
                st.error(
                    "Reviewer ID is required."
                )

            elif not human_confirmation:
                st.error(
                    "Human reviewer confirmation "
                    "is required."
                )

            else:

                result = submit_decision(
                    case_id=case_id,
                    decision="MORE_INFORMATION_REQUIRED",
                    human_approved=True,
                    reviewer_id=reviewer_id,
                    approval_token=(
                        f"HUMAN-{reviewer_id}"
                    ),
                )

                if result.get("success"):
                    st.success(
                        "Request for additional "
                        "information recorded."
                    )
                else:
                    st.error(
                        result.get(
                            "reason",
                            "Decision could not be recorded.",
                        )
                    )


    # --------------------------------------------------
    # DENY
    # --------------------------------------------------

    with action_col3:

        if st.button(
            "Deny",
            use_container_width=True,
        ):

            if not reviewer_id:
                st.error(
                    "Reviewer ID is required."
                )

            elif not human_confirmation:
                st.error(
                    "Human reviewer confirmation "
                    "is required for an adverse decision."
                )

            else:

                result = submit_decision(
                    case_id=case_id,
                    decision="DENIED",
                    human_approved=True,
                    reviewer_id=reviewer_id,
                    approval_token=(
                        f"HUMAN-{reviewer_id}"
                    ),
                )

                if result.get("success"):
                    st.success(
                        "Human adverse decision recorded."
                    )
                else:
                    st.error(
                        result.get(
                            "reason",
                            "Decision could not be recorded.",
                        )
                    )


    st.divider()

    st.caption(
        "AI prepares the case. "
        "The authorized clinician owns the final decision."
    )


else:

    st.info(
        "Select a case from the sidebar and click "
        "'Run Prior Authorization Review'."
    )