"""Streamlit viewer for the locally generated Red Team JSON report."""
import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="ARMS Red Team Dashboard", page_icon="🛡️", layout="wide")
st.title("ARMS – Agentic Red Team Dashboard")
st.caption("Local classroom simulator · synthetic data only · not a production security assessment")

report_path = Path(__file__).resolve().parents[1] / "reports" / "red_team_report.json"
if not report_path.exists():
    st.warning("No report found. Start the ARMS API and run: python -m orchestration.red_team --simulate-only")
    st.stop()

report = json.loads(report_path.read_text(encoding="utf-8"))
risk = report.get("final_risk", {})
eval_data = report.get("stage3", {}).get("robustness", {})
controls = report.get("stage3", {}).get("regulatory_matrix", {}).get("controls", [])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Risk score", f"{risk.get('score', 'N/A')}")
c2.metric("Severity", risk.get("severity", "N/A"))
c3.metric("Synthetic test pass rate", f"{eval_data.get('scenario_pass_rate', 0) * 100:.1f}%" if eval_data else "N/A")
c4.metric("Scenario cases", eval_data.get("cohort_size", "N/A"))

st.subheader("Five-agent assessment")
for key, agent in report.get("agents", {}).items():
    with st.expander(key.replace("_", " ").title()):
        st.write(agent.get("analysis", "No LLM analysis"))
        st.json(agent.get("evidence", {}))

if eval_data:
    st.subheader("Robustness evaluation")
    st.caption(eval_data.get("evaluation_scope", ""))
    st.dataframe(eval_data.get("cases", []), use_container_width=True)
    st.subheader("Threshold perturbations")
    st.dataframe(eval_data.get("threshold_perturbations", []), use_container_width=True)
    st.info("Precision and recall are calculated against authored synthetic scenario expectations, not verified fraud outcomes.")

if controls:
    st.subheader("Regulatory evidence matrix")
    st.dataframe(controls, use_container_width=True)
    st.caption(report.get("stage3", {}).get("regulatory_matrix", {}).get("disclaimer", ""))

with st.expander("Raw report"):
    st.json(report)
