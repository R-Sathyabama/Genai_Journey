import streamlit as st
from ingestion.db_loader import init_db
from engine.version_diff import get_changes_between
from engine.risk_engine import calculate_risk
from engine.intent_parser import detect_question_type
from engine.checklist_builder import build_checklist
from llm.grounded_explainer import generate_report

init_db()

st.title("🚀 DevOps Upgrade Intelligence Assistant")

tool = st.selectbox("Select Tool", ["kubernetes", "terraform", "helm", "docker"])
current_version = st.text_input("Current Version")
target_version = st.text_input("Target Version")
user_query = st.text_area("Your Question")

if st.button("Analyze Upgrade"):
    changes = get_changes_between(tool, current_version, target_version)

    st.write(f"🔍 Total Changes Found: {len(changes)}")

    risk = calculate_risk(changes)
    question_type = detect_question_type(user_query)

    report = generate_report(changes, question_type)
    checklist = build_checklist(changes)

    st.subheader("🧾 Upgrade Report")
    st.write(report)

    st.subheader("📋 Upgrade Checklist")
    for item in checklist:
        st.write("-", item)

    st.subheader("⚠ Overall Risk")
    st.write(risk)
