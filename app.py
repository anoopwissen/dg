# readiness_app_updated.py
# BCBS-239 Readiness Assessment – Fully Working Version with Timeliness Section

import streamlit as st
import pandas as pd
import datetime
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="BCBS-239 Readiness Assessment",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; }
.section-header {
    background: linear-gradient(90deg, #1f77b4 0%, #4a90d9 100%);
    color: white; padding: 0.75rem 1rem; border-radius: 0.5rem;
    margin: 1.5rem 0 1rem 0; font-weight: 600;
}
.metric-container {
    background: #f0f8ff; padding: 1rem; border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.gap-warning {
    background: #fff3cd; border-left: 4px solid #ffc107;
    padding: 0.75rem; border-radius: 0.25rem;
}
.success-message {
    background: #d4edda; border-left: 4px solid #28a745;
    padding: 0.75rem; border-radius: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

SCORE_MAP = {
    "Initial": 20,
    "Developing": 40,
    "Defined": 60,
    "Managed": 80,
    "Optimised": 100
}

SECTIONS = {
    "Governance & Ownership": {
        "weight": 0.20,
        "icon": "🏛️",
        "description": "Strategic oversight and accountability for risk data management",
        "questions": {
            "Is there clear data ownership defined for critical risk data elements?": {},
            "Have policies and procedures been updated to reflect BCBS-239 requirements?": {},
            "Is there a steering committee or oversight body assigned responsibility for risk data aggregation?": {}
        }
    },

    "Data Quality & Controls": {
        "weight": 0.25,
        "icon": "✓",
        "description": "Automated validation and monitoring of data accuracy and completeness",
        "questions": {
            "Are automated data quality rules implemented for Critical Data Elements (CDEs)?": {},
            "Do you measure and monitor data quality SLAs (timeliness, accuracy, completeness)?": {},
            "Are reconciliation processes defined and executed for risk figures (daily/monthly)?": {},
            "Is there an exception management process that tracks remediation and closure?": {}
        }
    },

    "Data Timeliness, SLA & Feed Controls": {
        "weight": 0.10,
        "icon": "⏱️",
        "description": "Timeliness, latency, SLA adherence, and governance of data feeds",
        "questions": {
            "Is the data feed frequency for this dataset formally defined and aligned with BCBS-239 reporting requirements?": {},
            "Are SLAs defined and monitored for data availability, timeliness, and completeness for this dataset?": {},
            "Is end-to-end data latency (source to reporting layer) defined, measured, and monitored?": {},
            "Are SLA or latency breaches automatically detected, logged, and remediated with audit evidence?": {},
            "Has data governance been formally applied to this dataset (ownership, lineage, data quality controls)?": {}
        }
    },

    "Lineage & Traceability": {
        "weight": 0.20,
        "icon": "🔍",
        "description": "End-to-end visibility of data flow from source to report",
        "questions": {
            "Can you demonstrate end-to-end lineage for each CDE from source to report?": {},
            "Is transformation logic documented, versioned, and accessible to auditors?": {},
            "Can you trace aggregated risk numbers back to source systems and transformations?": {}
        }
    },

    "BCBS-239 Specific Controls": {
        "weight": 0.20,
        "icon": "🎯",
        "description": "Controls specifically addressing BCBS-239 principle requirements",
        "questions": {
            "Is there a maintained catalogue of CDEs with owners and business definitions?": {},
            "Are aggregation rules across legal entities defined and validated?": {},
            "Do you perform stress or scenario checks to validate risk-data aggregation logic?": {},
            "Is there an independent validation function or second-line checks for key controls?": {}
        }
    },

    "Operational Resilience & Auditability": {
        "weight": 0.05,
        "icon": "🛡️",
        "description": "Incident response capability and audit trail completeness",
        "questions": {
            "Are runbooks and incident playbooks defined for data incidents affecting risk reporting?": {},
            "Is an audit trail available for changes to critical data and transformation logic?": {},
            "Are recovery and reconciliation SLAs defined for critical data flows?": {}
        }
    }
}

OPTIONS = ["Initial", "Developing", "Defined", "Managed", "Optimised"]

# ============================================================================
# STATE
# ============================================================================

def init_session_state():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "answers" not in st.session_state:
        st.session_state.answers = {}
        for s in SECTIONS.values():
            for q in s["questions"]:
                st.session_state.answers[q] = "Defined"

# ============================================================================
# LOGIC
# ============================================================================

def compute_scores():
    section_scores = {}
    for name, section in SECTIONS.items():
        scores = [SCORE_MAP[st.session_state.answers[q]] for q in section["questions"]]
        section_scores[name] = round(sum(scores) / len(scores))
    overall = round(sum(section_scores[s] * SECTIONS[s]["weight"] for s in section_scores))
    return section_scores, overall

# ============================================================================
# UI
# ============================================================================

def render_landing():
    st.markdown('<p class="main-header">📊 BCBS-239 Readiness Assessment</p>', unsafe_allow_html=True)
    if st.button("▶️ Start Assessment", type="primary"):
        st.session_state.started = True
        st.rerun()

def render_questions():
    for name, section in SECTIONS.items():
        st.markdown(f'<div class="section-header">{section["icon"]} {name}</div>', unsafe_allow_html=True)
        st.caption(section["description"])
        for q in section["questions"]:
            st.session_state.answers[q] = st.radio(q, OPTIONS, index=OPTIONS.index(st.session_state.answers[q]), horizontal=True)

def render_results(section_scores, overall):
    st.markdown("## 📊 Results")
    st.metric("Overall Readiness", f"{overall}%")
    df = pd.DataFrame({"Section": section_scores.keys(), "Score": section_scores.values()})
    st.bar_chart(df.set_index("Section"))

# ============================================================================
# MAIN
# ============================================================================

def main():
    init_session_state()

    if not st.session_state.started:
        render_landing()
    else:
        render_questions()
        section_scores, overall = compute_scores()
        render_results(section_scores, overall)

if __name__ == "__main__":
    main()
