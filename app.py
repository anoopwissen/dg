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

# Maturity to score mapping (1-5)
SCORE_MAP = {
    "Initial": 20,
    "Developing": 40,
    "Defined": 60,
    "Managed": 80,
    "Optimised": 100
}

# Sections and questions – all options updated to maturity levels
SECTIONS = {
    "Governance & Ownership": {
        "weight": 0.15,
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
    "Data Infrastructure & SLA Management": {
        "weight": 0.20,
        "icon": "⏱️",
        "description": "Data availability, timeliness, and service level compliance",
        "questions": {
            "Is the data feed frequency for this dataset formally defined, documented, and aligned with BCBS-239 reporting needs?": {
                "options": ["Initial", "Developin
