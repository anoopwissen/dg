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

# Sections and questions — all options updated to maturity levels
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
        "weight": 0.30,
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
                "guidance": "Formal rec processes with documented break resolution"
            },
            "Is there an exception management process that tracks remediation and closure?": {
                "options": ["Initial", "Developing", "Defined", "Managed", "Optimised"],
                "guidance": "Workflow system for logging, assigning, and closing exceptions"
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
        "weight": 0.10,
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

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    if "started" not in st.session_state:
        st.session_state.started = False
    
    if "answers" not in st.session_state:
        st.session_state.answers = {}
        # Default answer set to "Defined" (level 3). Change to "Initial" if you prefer empty baseline.
        for section_name, section_data in SECTIONS.items():
            for question in section_data["questions"].keys():
                st.session_state.answers[question] = "Defined"
    
    if "show_guidance" not in st.session_state:
        st.session_state.show_guidance = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_scores(answers_map):
    """Calculate section and overall scores"""
    section_scores = {}
    
    for section_name, section_data in SECTIONS.items():
        questions = list(section_data["questions"].keys())
        question_scores = [SCORE_MAP.get(answers_map[q], 0) for q in questions]
        avg_score = sum(question_scores) / len(question_scores) if question_scores else 0
        section_scores[section_name] = round(avg_score)
    
    overall = round(
        sum(section_scores[s] * SECTIONS[s]["weight"] for s in section_scores)
    )
    
    return section_scores, overall

def get_readiness_level(score):
    """Return readiness level based on score"""
    if score >= 90:
        return "Optimised", "🟢"
    elif score >= 75:
        return "Managed", "🔵"
    elif score >= 60:
        return "Defined", "🟡"
    elif score >= 40:
        return "Developing", "🟠"
    else:
        return "Initial", "🔴"

def generate_recommendations(section_scores):
    """Generate specific recommendations based on scores"""
    recommendations = []
    
    for section, score in section_scores.items():
        if score < 70:
            rec = {
                "section": section,
                "score": score,
                "priority": "High" if score < 50 else "Medium",
                "actions": []
            }
            
            if section == "Governance & Ownership":
                rec["actions"] = [
                    "Establish a BCBS-239 steering committee",
                    "Assign data owners for all CDEs",
                    "Update governance policies to reference BCBS-239"
                ]
            elif section == "Data Quality & Controls":
                rec["actions"] = [
                    "Implement automated DQ rules for CDEs",
                    "Define and monitor DQ SLAs",
                    "Establish exception management workflows"
                ]
            elif section == "Lineage & Traceability":
                rec["actions"] = [
                    "Document end-to-end lineage for all CDEs",
                    "Version control all transformation logic",
                    "Enable drill-down capability in reports"
                ]
            elif section == "BCBS-239 Specific Controls":
                rec["actions"] = [
                    "Create comprehensive CDE catalogue",
                    "Validate aggregation rules across entities",
                    "Implement independent validation checks"
                ]
            elif section == "Operational Resilience & Auditability":
                rec["actions"] = [
                    "Develop incident response runbooks",
                    "Enable complete audit trails",
                    "Define recovery SLAs for critical flows"
                ]
            
            recommendations.append(rec)
    
    return recommendations

def export_to_csv(answers_map, section_scores, overall_score):
    """Generate CSV export data"""
    export_rows = []
    
    for section_name, section_data in SECTIONS.items():
        for question, q_data in section_data["questions"].items():
            answer = answers_map[question]
            export_rows.append({
                "Section": section_name,
                "Question": question,
                "Answer": answer,
                "Score": SCORE_MAP.get(answer, 0),
                "Section_Score": section_scores[section_name],
                "Section_Weight": section_data["weight"]
            })
    
    df = pd.DataFrame(export_rows)
    df.attrs["overall_score"] = overall_score
    return df

def export_to_json(answers_map, section_scores, overall_score):
    """Generate JSON export data"""
    return {
        "assessment_metadata": {
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "app_version": "2.0",
            "assessment_type": "BCBS-239 Readiness"
        },
        "scores": {
            "overall": overall_score,
            "sections": section_scores
        },
        "answers": answers_map,
        "section_weights": {s: SECTIONS[s]["weight"] for s in SECTIONS}
    }

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_landing_page():
    """Render the landing/intro page"""
    st.markdown('<p class="main-header">📊 BCBS-239 Readiness Assessment</p>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the Wissen Accelerator Starter Kit
    
    This interactive assessment evaluates your organization's readiness for **BCBS-239** 
    (Basel Committee on Banking Supervision - Principles for effective risk data 
    aggregation and risk reporting).
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📋 What This Assessment Covers
        
        - **Governance & Ownership** (20%)
        - **Data Quality & Controls** (30%)
        - **Lineage & Traceability** (20%)
        - **BCBS-239 Specific Controls** (20%)
        - **Operational Resilience** (10%)
        
        **Duration:** 10-15 minutes  
        **Output:** Scored assessment with gap analysis and recommendations
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 How Wissen Can Help
        
        - Define Critical Data Elements (CDEs) and ownership
        - Build automated data quality rules and reconciliations
        - Implement end-to-end lineage and transformation tracking
        - Establish testable controls and validation workflows
        - Create operational runbooks and audit trails
        - Enable regulatory reporting compliance
        """)
    
    st.markdown("---")
    
    # Maturity Levels explanation (as requested)
    st.markdown("""
    ### 📘 Maturity Levels
    
    | Level | Name | Meaning |
    |------:|------|---------|
    | **1** | **Initial (Ad-hoc / Unstructured)** | Processes inconsistent, undocumented, reactive |
    | **2** | **Developing (Emerging Practices)** | Basic patterns forming, still inconsistent |
    | **3** | **Defined (Documented & Repeatable)** | Policies, procedures & controls documented |
    | **4** | **Managed (Integrated & Measurable)** | KPIs, SLAs, automation, monitoring in place |
    | **5** | **Optimised (Predictive & Continuous Compliance)** | Fully matured, continuously improved, predictive analytics |
    """)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("▶️  Start Assessment", type="primary", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    
    st.markdown("---")
    st.caption("💡 Tip: Use the 'Reset Assessment' button in the sidebar at any time to start over")

def render_questionnaire():
    """Render the main questionnaire"""
    st.markdown('<p class="main-header">📋 BCBS-239 Readiness Questionnaire</p>', 
                unsafe_allow_html=True)
    
    total_questions = sum(len(s["questions"]) for s in SECTIONS.values())
    # Since default answers are set, we consider any selection as answered
    answered_questions = len(st.session_state.answers)
    progress = answered_questions / total_questions if total_questions > 0 else 0
    
    st.progress(progress, text=f"Progress: {answered_questions}/{total_questions} questions (all questions pre-populated; adjust as needed)")
    
    st.markdown("---")
    
    for section_name, section_data in SECTIONS.items():
        st.markdown(
            f'<div class="section-header">{section_data["icon"]} {section_name}</div>',
            unsafe_allow_html=True
        )
        st.caption(section_data["description"])
        
        for question, q_data in section_data["questions"].items():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                current_answer = st.session_state.answers.get(question, "Defined")
                # Determine index safely
                try:
                    index = q_data["options"].index(current_answer)
                except ValueError:
                    index = 2  # fallback to "Defined"
                new_answer = st.radio(
                    question,
                    options=q_data["options"],
                    index=index,
                    key=f"q_{section_name}_{hash(question)}",
                    horizontal=True
                )
                st.session_state.answers[question] = new_answer
            
            with col2:
                guidance_key = f"guidance_{section_name}_{hash(question)}"
                if st.button("💡 Guidance", key=guidance_key, use_container_width=True):
                    st.session_state.show_guidance[question] = not st.session_state.show_guidance.get(question, False)
            
            if st.session_state.show_guidance.get(question, False):
                st.info(f"**Guidance:** {q_data['guidance']}")
        
        st.markdown("<br>", unsafe_allow_html=True)

def render_results(section_scores, overall_score):
    """Render results and analytics"""
    st.markdown("---")
    st.markdown('<p class="main-header">📊 Assessment Results</p>', unsafe_allow_html=True)
    
    # Overall score display
    col1, col2, col3, col4 = st.columns(4)
    
    level, icon = get_readiness_level(overall_score)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Overall Readiness", f"{overall_score}%", delta=f"{level} {icon}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        max_section = max(section_scores, key=section_scores.get)
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Strongest Area", max_section[:20] + "...", f"{section_scores[max_section]}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        min_section = min(section_scores, key=section_scores.get)
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Priority Focus", min_section[:20] + "...", f"{section_scores[min_section]}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        gaps = sum(1 for s in section_scores.values() if s < 70)
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Gaps Identified", gaps, delta="sections below 70%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed section breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Section Performance")
        
        # Create visualization dataframe
        viz_data = pd.DataFrame({
            "Section": list(section_scores.keys()),
            "Score": list(section_scores.values()),
            "Weight": [SECTIONS[s]["weight"] * 100 for s in section_scores.keys()]
        })
        
        st.bar_chart(viz_data.set_index("Section")["Score"])
        
        # Detailed table
        st.markdown("**Detailed Breakdown**")
        display_df = viz_data.copy()
        display_df["Score"] = display_df["Score"].apply(lambda x: f"{x}%")
        display_df["Weight"] = display_df["Weight"].apply(lambda x: f"{x:.0f}%")
        st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Recommendations")
        
        recommendations = generate_recommendations(section_scores)
        
        if recommendations:
            for rec in recommendations:
                priority_color = "🔴" if rec["priority"] == "High" else "🟡"
                st.markdown(
                    f'<div class="gap-warning">'
                    f'<strong>{priority_color} {rec["section"]}</strong><br>'
                    f'Score: {rec["score"]}% | Priority: {rec["priority"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                with st.expander("View recommended actions"):
                    for action in rec["actions"]:
                        st.markdown(f"• {action}")
        else:
            st.markdown(
                '<div class="success-message">'
                '✅ <strong>Excellent!</strong><br>No critical gaps identified. '
                'Continue monitoring and maintaining controls.'
                '</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Export buttons
        st.subheader("📥 Export Results")
        
        csv_data = export_to_csv(st.session_state.answers, section_scores, overall_score)
        json_data = export_to_json(st.session_state.answers, section_scores, overall_score)
        
        st.download_button(
            "⬇️ Download CSV Report",
            csv_data.to_csv(index=False),
            f"bcbs239_assessment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True
        )
        
        st.download_button(
            "⬇️ Download JSON Report",
            json.dumps(json_data, indent=2),
            f"bcbs239_assessment_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json",
            use_container_width=True
        )

def render_question_details(section_scores):
    """Render detailed question-level analysis"""
    st.markdown("---")
    st.subheader("📋 Detailed Question Analysis")
    
    question_data = []
    for section_name, section_data in SECTIONS.items():
        for question in section_data["questions"].keys():
            answer = st.session_state.answers[question]
            question_data.append({
                "Section": section_name,
                "Question": question,
                "Answer": answer,
                "Score": SCORE_MAP.get(answer, 0),
                "Section Score": section_scores[section_name]
            })
    
    df = pd.DataFrame(question_data)
    
    # Color coding for answers — map maturity to colors
    def highlight_answers(row):
        colors = {
            "Initial": "#f8d7da",      # red
            "Developing": "#fff3cd",   # yellow
            "Defined": "#e2e3ff",      # light blue
            "Managed": "#d1ecf1",      # cyan-ish
            "Optimised": "#d4edda"     # green
        }
        color = colors.get(row["Answer"], "")
        return [f'background-color: {color}'] * len(row)
    
    styled_df = df.style.apply(highlight_answers, axis=1)
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application logic"""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        if st.session_state.started:
            if st.button("🔄 Reset Assessment", use_container_width=True):
                st.session_state.started = False
                st.session_state.answers = {}
                st.rerun()
            
            st.markdown("---")
            st.markdown("### ℹ️ About This Assessment")
            st.markdown("""
            This tool evaluates your organization's readiness across five key 
            dimensions of BCBS-239 compliance.
            
            **Scoring (Maturity Levels):**
            - 1️⃣ Initial (Ad-hoc / Unstructured) — 20 points  
            - 2️⃣ Developing (Emerging Practices) — 40 points  
            - 3️⃣ Defined (Documented & Repeatable) — 60 points  
            - 4️⃣ Managed (Integrated & Measurable) — 80 points  
            - 5️⃣ Optimised (Predictive & Continuous Compliance) — 100 points
            """)
        else:
            st.markdown("""
            ### 🚀 Quick Start
            
            1. Click "Start Assessment"
            2. Answer all questions
            3. Review your scores
            4. Export results
            5. Act on recommendations
            """)
        
        st.markdown("---")
        st.caption("**Wissen Accelerator** | BCBS-239 Starter Kit v2.0")
    
    # Main content
    if not st.session_state.started:
        render_landing_page()
    else:
        render_questionnaire()
        
        # Calculate scores
        section_scores, overall_score = compute_scores(st.session_state.answers)
        
        # Render results
        render_results(section_scores, overall_score)
        render_question_details(section_scores)
        
        # Footer
        st.markdown("---")
        st.caption(
            "💡 **Next Steps:** Integrate with your data governance tools "
            "(Collibra, Informatica, Microsoft Purview) for automated monitoring "
            "and continuous compliance tracking."
        )

if __name__ == "__main__":
    main()
