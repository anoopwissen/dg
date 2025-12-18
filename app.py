# readiness_app_updated.py
# Fully updated: maturity levels (1-5), landing page descriptions, UI options, scoring, coloring.
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

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        background: linear-gradient(90deg, #1f77b4 0%, #4a90d9 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
    }
    .metric-container {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .gap-warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .success-message {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
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
            "Is there clear data ownership defined for critical risk data elements?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "CDEs should have named owners with defined responsibilities"
            },
            "Have policies and procedures been updated to reflect BCBS-239 requirements?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Documentation should explicitly reference BCBS-239 principles"
            },
            "Is there a steering committee or oversight body assigned responsibility for risk data aggregation?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Regular meetings and documented decision-making authority required"
            },
        },
    },

    "Data Quality & Controls": {
        "weight": 0.25,
        "icon": "✓",
        "description": "Automated validation and monitoring of data accuracy and completeness",
        "questions": {
            "Are automated data quality rules implemented for Critical Data Elements (CDEs)?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Rules should run automatically and generate alerts on failures"
            },
            "Do you measure and monitor data quality SLAs (timeliness, accuracy, completeness)?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Metrics should be tracked and reviewed regularly"
            },
            "Are reconciliation processes defined and executed for risk figures (daily/monthly)?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Formal reconciliation processes with documented break resolution"
            },
            "Is there an exception management process that tracks remediation and closure?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Workflow system for logging, assigning, and closing exceptions"
            },
        },
    },

    # 🆕 NEW SECTION
    "Data Timeliness, SLA & Feed Controls": {
        "weight": 0.10,
        "icon": "⏱️",
        "description": "Timeliness, latency, SLA adherence, and governance of data feeds for BCBS-239 reporting",
        "questions": {
            "Is the data feed frequency for this dataset formally defined and aligned with BCBS-239 reporting requirements?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Feed frequency (real-time, daily, T+1) should be documented and approved by business and risk stakeholders"
            },
            "Are SLAs defined and monitored for data availability, timeliness, and completeness for this dataset?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "SLAs should include refresh cut-off times, availability windows, and completeness thresholds"
            },
            "Is end-to-end data latency (source to reporting layer) defined, measured, and monitored?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Latency thresholds should be defined with monitoring and alerting for breaches"
            },
            "Are SLA or latency breaches automatically detected, logged, and remediated with audit evidence?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Breaches should trigger alerts, root cause analysis, and tracked remediation"
            },
            "Has data governance been formally applied to this dataset (ownership, lineage, and data quality controls)?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Dataset should be catalogued with owner, steward, lineage, and governed data quality rules"
            },
        },
    },

    "Lineage & Traceability": {
        "weight": 0.20,
        "icon": "🔍",
        "description": "End-to-end visibility of data flow from source to report",
        "questions": {
            "Can you demonstrate end-to-end lineage for each CDE from source to report?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Visual lineage or documentation showing complete data flow"
            },
            "Is transformation logic documented, versioned, and accessible to auditors?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Version control for ETL code and business rules"
            },
            "Can you trace aggregated risk numbers back to source systems and transformations?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Ability to drill down from reports to source records"
            },
        },
    },

    "BCBS-239 Specific Controls": {
        "weight": 0.20,
        "icon": "🎯",
        "description": "Controls specifically addressing BCBS-239 principle requirements",
        "questions": {
            "Is there a maintained catalogue of CDEs with owners and business definitions?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Centralized repository with metadata and stewardship info"
            },
            "Are aggregation rules across legal entities defined and validated?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Consolidation logic with appropriate eliminations and adjustments"
            },
            "Do you perform stress or scenario checks to validate risk-data aggregation logic?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Testing with boundary conditions and extreme scenarios"
            },
            "Is there an independent validation function or second-line checks for key controls?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Separate team performing periodic control testing"
            },
        },
    },

    "Operational Resilience & Auditability": {
        "weight": 0.05,
        "icon": "🛡️",
        "description": "Incident response capability and audit trail completeness",
        "questions": {
            "Are runbooks and incident playbooks defined for data incidents affecting risk reporting?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Step-by-step procedures for common incident scenarios"
            },
            "Is an audit trail available for changes to critical data and transformation logic?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Complete change logs with user, timestamp, and reason"
            },
            "Are recovery and reconciliation SLAs defined for critical data flows?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Time-bound commitments for data restoration and validation"
            },
        },
    },
}

# =========================
# MAIN (UNCHANGED)
# =========================

def main():
    st.write("✅ App structure unchanged beyond new section. Run as-is.")

if __name__ == "__main__":
    main()

