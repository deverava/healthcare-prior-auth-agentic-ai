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


# --------------------------------------------------
# FINAL REVIEWER WORKBENCH — SECOND MOCKUP
# --------------------------------------------------

from html import escape


def _h(value):
    return escape(str(value if value is not None else "N/A"))


def _recommendation_parts(state):
    raw = state.get("recommendation")
    rationale = state.get("rationale")

    if isinstance(raw, dict):
        return (
            raw.get("recommendation", "No recommendation available"),
            raw.get("rationale") or rationale or "",
        )

    return raw or "No recommendation available", rationale or ""


def _status_counts(criteria):
    total = len(criteria)
    met = sum(
        1 for item in criteria
        if str(item.get("status", "")).strip().lower() == "met"
    )
    return total, met


st.markdown(
    """
    <style>
    :root {
        --navy:#0b2a66;
        --blue:#0877e8;
        --blue2:#0b63c9;
        --pale:#eef6ff;
        --line:#d7e5f5;
        --text:#102a56;
        --muted:#5e7191;
        --green:#07885b;
        --greenbg:#eafaf3;
        --amber:#dc7900;
        --amberbg:#fff6e7;
        --red:#c9365a;
        --redbg:#fff0f4;
    }

    .stApp {background:#f7fbff;}
    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background:#ffffff;
        border-right:1px solid #d8e5f4;
    }
    [data-testid="stSidebar"] .block-container {padding-top:1rem;}
    [data-testid="stSidebar"] button {border-radius:10px;}

    .topbar {
        background:linear-gradient(100deg,#0877e8 0%,#0756a8 58%,#06447e 100%);
        border-radius:0 0 14px 14px;
        color:white;
        padding:1rem 1.25rem;
        margin:0 0 1rem 0;
        box-shadow:0 5px 16px rgba(4,67,132,.18);
    }
    .top-title {font-size:1.75rem;font-weight:850;line-height:1.1;}
    .top-sub {font-size:.9rem;opacity:.92;margin-top:.28rem;}
    .top-badges {font-size:.78rem;opacity:.95;text-align:right;padding-top:.3rem;}

    .side-brand {
        color:#102a56;font-weight:850;font-size:1.05rem;
        padding:.25rem 0 .7rem 0;
    }
    .side-nav {
        border-radius:10px;padding:.65rem .75rem;margin:.2rem 0;
        color:#183a72;font-weight:650;
    }
    .side-nav.active {background:#e7f2ff;color:#0769d6;}
    .case-card {
        border:1px solid #e1eaf5;border-radius:10px;padding:.7rem .75rem;
        margin:.45rem 0;background:white;
    }
    .case-card.active {
        border-left:5px solid #0877e8;background:#eaf4ff;
    }
    .case-id {font-weight:850;color:#102a56;}
    .case-service {font-size:.82rem;color:#244b82;margin-top:.1rem;}
    .case-meta {font-size:.72rem;color:#6c7f9d;margin-top:.18rem;}

    .metric-card {
        min-height:105px;border:1px solid var(--line);border-radius:12px;
        padding:.9rem 1rem;background:white;box-shadow:0 2px 8px rgba(17,67,120,.04);
    }
    .metric-blue {background:#eaf4ff;}
    .metric-purple {background:#f3efff;}
    .metric-amber {background:#fff5e5;}
    .metric-mint {background:#eafaf5;}
    .metric-label {
        font-size:.72rem;color:#536d92;font-weight:700;
        letter-spacing:.03em;
    }
    .metric-value {font-size:1.3rem;color:#102a56;font-weight:850;margin-top:.25rem;}
    .metric-sub {font-size:.78rem;color:#46648d;margin-top:.12rem;}

    .info-strip {
        border:1px solid var(--line);border-radius:12px;background:white;
        padding:.9rem 1rem;margin:.75rem 0;
    }
    .info-title {font-weight:850;color:#0b2a66;margin-bottom:.55rem;font-size:1rem;}
    .kv-row {
        display:grid;grid-template-columns:130px 1fr;gap:.35rem;
        padding:.17rem 0;font-size:.82rem;color:#294b7c;
    }
    .kv-row span:first-child {color:#5f7394;}

    .panel {
        border:1px solid var(--line);border-radius:12px;background:white;
        padding:1rem;margin:.55rem 0;box-shadow:0 2px 8px rgba(17,67,120,.035);
    }
    .panel-title {font-size:1.05rem;font-weight:850;color:#0b2a66;margin-bottom:.65rem;}
    .soft-blue {background:#edf5ff;border-radius:9px;padding:.75rem .85rem;}
    .soft-purple {background:#f4efff;border-radius:9px;padding:.75rem .85rem;}
    .soft-green {background:var(--greenbg);border-radius:9px;padding:.8rem .9rem;}
    .soft-amber {background:var(--amberbg);border-radius:9px;padding:.8rem .9rem;}

    .mini-grid {display:grid;grid-template-columns:repeat(4,1fr);gap:.65rem;margin-top:.75rem;}
    .mini {
        border:1px solid var(--line);border-radius:10px;padding:.7rem;
        background:#f8fbff;
    }
    .mini.green {background:#ebfaf4;}
    .mini.purple {background:#f3efff;}
    .mini.red {background:#fff0f4;}
    .mini-label {font-size:.7rem;color:#607798;}
    .mini-value {font-size:1.05rem;font-weight:850;color:#102a56;margin-top:.2rem;}

    .recommend {
        background:linear-gradient(100deg,#e9fbf3,#f2fcf8);
        border:1px solid #bfead6;border-radius:12px;padding:1rem;
    }
    .recommend-title {font-size:1.12rem;font-weight:850;color:#086844;}
    .recommend-copy {font-size:.86rem;color:#315f52;margin-top:.35rem;}
    .warning-box {
        background:#fff7e9;border:1px solid #efd39c;border-radius:10px;
        padding:.8rem .9rem;margin-top:.7rem;color:#684b18;font-size:.84rem;
    }

    .criteria {
        border:1px solid var(--line);border-radius:10px;padding:.75rem .85rem;
        margin:.45rem 0;background:white;
    }
    .criteria.met {border-left:5px solid #079264;background:#effbf6;}
    .criteria.warn {border-left:5px solid #e39b16;background:#fff9ec;}
    .criteria.conflict {border-left:5px solid #cf3f5f;background:#fff2f5;}
    .pill {
        display:inline-block;border-radius:999px;padding:.15rem .5rem;
        font-size:.68rem;font-weight:850;margin-left:.45rem;
    }
    .pill.green {background:#d9f5e8;color:#08734e;}
    .pill.amber {background:#ffedbd;color:#835a00;}
    .pill.red {background:#ffdce4;color:#9a2942;}

    .timeline-item {
        border-left:3px solid #21a578;padding:.15rem 0 .75rem .75rem;
        color:#294b7c;font-size:.82rem;
    }
    .timeline-item.last {border-left-color:#e19b18;}
    .timeline-time {float:right;color:#7185a4;font-size:.72rem;}

    div[data-testid="stTabs"] button {
        font-weight:750;color:#31557f;padding-left:1rem;padding-right:1rem;
    }
    div[data-testid="stTabs"] [aria-selected="true"] {color:#0877e8;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown(
    '<div class="side-brand">✚ &nbsp; Prior Authorization<br>'
    '<span style="font-size:.78rem;font-weight:500;">Reviewer Workbench</span></div>',
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="side-nav active">▣ &nbsp; Review Queue</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="side-nav">◷ &nbsp; Case History</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="side-nav">▥ &nbsp; Analytics</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="side-nav">▤ &nbsp; Audit Logs</div>', unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("### Search Cases")

case_options = {}
case_metadata = {}

for case_file in sorted(CASE_FOLDER.glob("*.json")):
    try:
        with open(case_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        cid = data.get("case_id", "Unknown")
        service = data.get("requested_service", {}).get("procedure_name", "Unknown Service")
        urgency = data.get("urgency", "standard").title()
        label = f"{cid} | {service}"
        case_options[label] = case_file.name
        case_metadata[label] = (cid, service, urgency, data.get("request_date", ""))
    except (json.JSONDecodeError, OSError):
        continue

selected_label = st.sidebar.selectbox(
    "Case",
    list(case_options.keys()),
    label_visibility="collapsed",
)
selected_file = case_options[selected_label]

if st.sidebar.button("Open Selected Case", type="primary", use_container_width=True):
    selected_case = load_case(selected_file)
    with st.spinner("Preparing clinical review packet..."):
        selected_state = run_workflow(selected_case)
    st.session_state["case"] = selected_case
    st.session_state["state"] = selected_state

st.sidebar.markdown("#### Review Queue")
for label, meta in case_metadata.items():
    cid, service, urgency, request_date = meta
    active = " active" if label == selected_label else ""
    st.sidebar.markdown(
        f"""
        <div class="case-card{active}">
          <div class="case-id">{_h(cid)}</div>
          <div class="case-service">{_h(service)}</div>
          <div class="case-meta">{_h(urgency)} &nbsp; | &nbsp; {_h(request_date)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown(
    """
    <div style="margin-top:1rem;background:#eaf4ff;border-radius:12px;padding:.85rem;color:#16467f;">
      <b>♥ Better Decisions<br>Healthier Lives</b>
      <div style="font-size:.76rem;margin-top:.35rem;">AI prepares the review. The clinician makes the decision.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# MAIN
# --------------------------------------------------

st.markdown(
    """
    <div class="topbar">
      <div style="display:grid;grid-template-columns:1.5fr 1fr;gap:1rem;">
        <div>
          <div class="top-title">✚ &nbsp; Healthcare Prior Authorization Reviewer</div>
          <div class="top-sub">AI-assisted clinical decision support with mandatory human review.</div>
        </div>
        <div class="top-badges">◈ Patient-Centered &nbsp;&nbsp; ▣ Evidence-Based &nbsp;&nbsp; ▥ Policy-Driven &nbsp;&nbsp; 🔒 Human-Controlled</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "case" not in st.session_state or "state" not in st.session_state:
    st.info("Choose a case in the Review Queue and click **Open Selected Case**.")
else:
    case = st.session_state["case"]
    state = st.session_state["state"]

    cid = case.get("case_id", "Unknown Case")
    urgency = case.get("urgency", "standard").title()
    request_date = case.get("request_date", "N/A")
    member = case.get("member", {})
    service = case.get("requested_service", {})
    insurance = case.get("insurance", {})
    policy = state.get("policy", {})
    criteria = state.get("criteria_matrix", [])
    verification = state.get("verification", {})
    recommendation, rationale = _recommendation_parts(state)
    total_criteria, met_criteria = _status_counts(criteria)
    documents = case.get("clinical_documents", [])
    missing_docs = state.get("missing_evidence", [])

    # Top cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card metric-blue"><div class="metric-label">Case ID</div>'
            f'<div class="metric-value">▣ {_h(cid)}</div>'
            f'<div class="metric-sub">{_h(service.get("procedure_name","N/A"))}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card metric-purple"><div class="metric-label">Priority</div>'
            f'<div class="metric-value">⚑ {_h(urgency)}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            '<div class="metric-card metric-amber"><div class="metric-label">Status</div>'
            '<div class="metric-value" style="color:#b85b00;">⚠ HUMAN REVIEW REQUIRED</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card metric-mint"><div class="metric-label">Received</div>'
            f'<div class="metric-value">▦ {_h(request_date)}</div>'
            f'<div class="metric-sub">Prior authorization request</div></div>',
            unsafe_allow_html=True,
        )

    # Member / service / coverage strip
    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(
            f"""
            <div class="info-strip">
              <div class="info-title">● &nbsp; Patient / Member Information</div>
              <div class="kv-row"><span>Member ID</span><b>{_h(member.get("member_id","N/A"))}</b></div>
              <div class="kv-row"><span>Date of Birth</span><b>{_h(member.get("date_of_birth","N/A"))}</b></div>
              <div class="kv-row"><span>Plan</span><b>{_h(insurance.get("plan_name","N/A"))}</b></div>
            </div>
            """, unsafe_allow_html=True)
    with i2:
        st.markdown(
            f"""
            <div class="info-strip">
              <div class="info-title">🩺 &nbsp; Requested Service</div>
              <div class="kv-row"><span>Procedure</span><b>{_h(service.get("procedure_name","N/A"))}</b></div>
              <div class="kv-row"><span>Procedure Code</span><b>{_h(service.get("procedure_code","N/A"))}</b></div>
              <div class="kv-row"><span>Diagnosis</span><b>{_h(service.get("diagnosis","N/A"))}</b></div>
              <div class="kv-row"><span>Diagnosis Code</span><b>{_h(service.get("diagnosis_code","N/A"))}</b></div>
              <div class="kv-row"><span>Body Site</span><b>{_h(service.get("body_site","N/A"))}</b></div>
            </div>
            """, unsafe_allow_html=True)
    with i3:
        st.markdown(
            f"""
            <div class="info-strip">
              <div class="info-title">🛡 &nbsp; Insurance / Coverage</div>
              <div class="kv-row"><span>Payer</span><b>{_h(insurance.get("payer","N/A"))}</b></div>
              <div class="kv-row"><span>Plan</span><b>{_h(insurance.get("plan_name","N/A"))}</b></div>
              <div class="kv-row"><span>Product Code</span><b>{_h(insurance.get("product_code","N/A"))}</b></div>
              <div class="kv-row"><span>Effective</span><b>{_h(insurance.get("coverage_effective_date","N/A"))}</b></div>
            </div>
            """, unsafe_allow_html=True)

    overview_tab, policy_tab, criteria_tab, decision_tab, audit_tab = st.tabs(
        ["⌂ Overview", "▤ Evidence & Policy", "☑ Clinical Criteria", "● Decision", "◷ Audit Trail"]
    )

    # OVERVIEW
    with overview_tab:
        left, right = st.columns([2, 1])

        with left:
            st.markdown('<div class="panel"><div class="panel-title">▣ Case Summary</div>', unsafe_allow_html=True)
            st.write(
                f"Prior authorization request for **{service.get('procedure_name','N/A')}** "
                f"for **{service.get('diagnosis','N/A')}**. The workflow resolved the applicable "
                "policy, extracted clinical evidence, evaluated documentation completeness, "
                "mapped evidence to criteria, and performed independent verification."
            )
            st.markdown(
                f"""
                <div class="mini-grid">
                  <div class="mini green"><div class="mini-label">Documents</div><div class="mini-value">{len(documents)}</div><div class="mini-label">Processed</div></div>
                  <div class="mini purple"><div class="mini-label">Clinical Criteria</div><div class="mini-value">{total_criteria}</div><div class="mini-label">Evaluated</div></div>
                  <div class="mini"><div class="mini-label">Criteria Status</div><div class="mini-value">{met_criteria} / {total_criteria}</div><div class="mini-label">Met</div></div>
                  <div class="mini red"><div class="mini-label">AI Recommendation</div><div class="mini-value" style="font-size:.88rem;">{_h(recommendation)}</div><div class="mini-label">Human review required</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="panel"><div class="panel-title">🤖 AI Decision-Support Summary</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="recommend">
                  <div style="font-size:1.12rem;font-weight:850;color:#08734e;">✓ {_h(recommendation)}</div>
                  <div class="recommend-copy">{_h(rationale or "Review the evidence and policy criteria before making the final determination.")}</div>
                </div>
                <div class="warning-box"><b>⚠ Important</b><br>
                This is <b>not</b> the final authorization decision. A qualified clinical reviewer must review the evidence and make the final determination.</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel"><div class="panel-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
            st.button("View Policy Details", use_container_width=True)
            st.button("Open Clinical Criteria", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="panel"><div class="panel-title">◷ Case Timeline</div>', unsafe_allow_html=True)
            timeline = [
                "Case Received",
                "Policy Selected",
                "Evidence Extracted",
                "Criteria Evaluated",
                "AI Recommendation",
            ]
            for item in timeline:
                st.markdown(f'<div class="timeline-item">✓ &nbsp; {_h(item)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="timeline-item last">● &nbsp; <b>Awaiting Human Review</b></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # EVIDENCE & POLICY
    with policy_tab:
        left, right = st.columns([1.35, 1])

        with left:
            st.markdown('<div class="panel"><div class="panel-title">▤ Selected Policy</div>', unsafe_allow_html=True)
            if policy:
                st.markdown(
                    f"""
                    <div style="font-size:1.12rem;font-weight:850;color:#0b2a66;">{_h(policy.get("policy_name","N/A"))}</div>
                    <div class="kv-row"><span>Policy ID</span><b>{_h(policy.get("policy_id","N/A"))}</b></div>
                    <div class="kv-row"><span>Version</span><b>{_h(policy.get("version","N/A"))}</b></div>
                    <div class="kv-row"><span>Effective</span><b>{_h(policy.get("effective_date","N/A"))} → {_h(policy.get("expiration_date","N/A"))}</b></div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="soft-purple" style="margin-top:.75rem;">
                      <b>Policy Service Mapping</b><br>
                      Procedure Code: <b>{_h(service.get("procedure_code","N/A"))}</b><br>
                      Service: <b>{_h(service.get("procedure_name","N/A"))}</b><br>
                      Criteria evaluated: <b>{total_criteria}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("No valid policy was resolved.")
            st.markdown("</div>", unsafe_allow_html=True)

            if missing_docs:
                st.warning("Additional documentation is required: " + ", ".join(map(str, missing_docs)))
            else:
                st.success("✓ Required documentation is complete.")

        with right:
            st.markdown('<div class="panel"><div class="panel-title">▣ Supporting Documentation</div>', unsafe_allow_html=True)
            for doc in documents:
                st.markdown(
                    f"""
                    <div class="case-card">
                      <div class="case-id">{_h(doc.get("document_type","Clinical Document"))}</div>
                      <div class="case-meta">{_h(doc.get("document_id","N/A"))} &nbsp; • &nbsp; {_h(doc.get("document_date","N/A"))}</div>
                      <div style="margin-top:.25rem;color:#07885b;font-size:.75rem;font-weight:750;">✓ Processed</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # CLINICAL CRITERIA
    with criteria_tab:
        st.markdown("### Clinical Criteria Evaluation")
        for item in criteria:
            status = str(item.get("status", "Unknown"))
            low = status.lower()
            if low == "met":
                cls, pill, icon = "met", "green", "✓"
            elif "conflict" in low:
                cls, pill, icon = "conflict", "red", "!"
            else:
                cls, pill, icon = "warn", "amber", "⚠"

            st.markdown(
                f"""
                <div class="criteria {cls}">
                  <b>{icon} {_h(item.get("criterion_id","Unknown"))}</b>
                  <span class="pill {pill}">{_h(status)}</span>
                  <div style="margin-top:.35rem;color:#405d82;">{_h(item.get("description",""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            evidence = item.get("evidence", [])
            conflicts = item.get("conflicting_evidence", [])
            if evidence or conflicts:
                with st.expander(f"Evidence for {item.get('criterion_id','criterion')}"):
                    for ev in evidence:
                        st.write(
                            f"**{ev.get('document_type','Document')}** "
                            f"({ev.get('document_id','N/A')})"
                        )
                        if ev.get("source_text"):
                            st.info(ev.get("source_text"))
                        if ev.get("confidence"):
                            st.caption(f"Confidence: {ev.get('confidence')}")
                    for ev in conflicts:
                        st.warning(ev.get("source_text", "Conflicting evidence detected."))

        st.divider()
        if verification.get("verification_passed"):
            st.success("✓ Independent verification passed.")
        else:
            st.warning("Independent verification requires human review.")
            for issue in verification.get("issues", []):
                st.write(f"• {issue}")

    # DECISION
    with decision_tab:
        st.markdown("### Human Clinical Decision")
        st.markdown(
            f"""
            <div class="recommend">
              <div style="font-size:.75rem;font-weight:850;color:#08734e;">AI DECISION-SUPPORT RECOMMENDATION</div>
              <div style="font-size:1.2rem;font-weight:850;color:#086844;margin-top:.25rem;">✓ {_h(recommendation)}</div>
              <div class="recommend-copy">{_h(rationale)}</div>
            </div>
            <div class="warning-box"><b>Human review required.</b> The AI output is advisory and cannot make the final authorization decision.</div>
            """,
            unsafe_allow_html=True,
        )

        reviewer_id = st.text_input("Reviewer ID", placeholder="Example: CLINICIAN-001")
        human_confirmation = st.checkbox(
            "I confirm that I am the authorized human reviewer for this case."
        )

        a, b, c = st.columns(3)
        with a:
            approve = st.button("✓ Approve", type="primary", use_container_width=True)
        with b:
            more_info = st.button("Request More Information", use_container_width=True)
        with c:
            deny = st.button("Deny", use_container_width=True)

        def record_human_decision(decision, success_message, adverse=False):
            if not reviewer_id:
                st.error("Reviewer ID is required.")
                return
            if not human_confirmation:
                st.error(
                    "Human reviewer confirmation is required"
                    + (" for an adverse decision." if adverse else ".")
                )
                return
            result = submit_decision(
                case_id=cid,
                decision=decision,
                human_approved=True,
                reviewer_id=reviewer_id,
                approval_token=f"HUMAN-{reviewer_id}",
            )
            if result.get("success"):
                st.success(success_message)
            else:
                st.error(result.get("reason", "Decision could not be recorded."))

        if approve:
            record_human_decision("APPROVED", "Human approval recorded.")
        if more_info:
            record_human_decision(
                "MORE_INFORMATION_REQUIRED",
                "Request for additional information recorded.",
            )
        if deny:
            record_human_decision(
                "DENIED",
                "Human adverse decision recorded.",
                adverse=True,
            )

    # AUDIT TRAIL
    with audit_tab:
        st.markdown("### Audit Trail")
        st.info(
            "The workflow records governed processing events in the audit log, "
            "including intake, policy selection, evidence extraction, completeness, "
            "criteria evaluation, verification, recommendation creation, and human review."
        )
        st.code(
            "INTAKE\n"
            "POLICY_SELECTED\n"
            "EVIDENCE_EXTRACTED\n"
            "COMPLETENESS_EVALUATED\n"
            "CRITERIA_EVALUATED\n"
            "VERIFICATION_COMPLETED\n"
            "RECOMMENDATION_CREATED\n"
            "HUMAN_REVIEW",
            language="text",
        )
