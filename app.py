import os
from typing import Dict

import streamlit as st

from orchestrator import run_workflow

st.set_page_config(page_title="RiskRadar AI", page_icon="🛡️", layout="wide")


def build_profile(form_data: Dict[str, object]) -> Dict[str, object]:
    return {
        "industry": form_data.get("industry", "Technology"),
        "region": form_data.get("region", "Global"),
        "incident_summary": form_data.get("incident_summary", "No recent incidents"),
    }


def render_workflow(result: Dict[str, object]) -> None:
    st.subheader("Executive view")
    summary = result["summary"]
    st.caption(f"Department: {summary.get('selected_department', 'N/A')} | Region: {summary.get('selected_region', 'N/A')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Top emerging risks", ", ".join(summary["top_risks"]))
    col2.metric("Highest exposure", summary["highest_exposure"])
    col3.metric("Exposure value", f"${summary['exposure_value']:,}")

    st.metric("Risk outlook", summary["risk_outlook"])
    st.metric("Derived claim count", summary["derived_claim_count"])
    st.metric("Derived claim amount", f"${summary['derived_claim_amount']:,}")
    st.metric("Derived loss ratio", f"{summary['derived_loss_ratio']:.2f}%")

    with st.expander("Exposed companies"):
        for record in summary["exposed_companies"]:
            st.write(f"- {record['cedent']} ({record['region']})")

    with st.expander("Recent incident summary"):
        st.write(summary.get("recent_incident_summary", "No recent incidents"))

    with st.expander("Executive report"):
        st.write(summary["report_summary"])

    with st.expander("Recommended actions"):
        for action in summary["recommended_actions"]:
            st.write(f"- {action}")

    st.subheader("Agent execution trail")
    for agent in result["workflow"]:
        with st.expander(agent["agent"]):
            st.write(agent["summary"])
            st.json(agent["output"])


def main() -> None:
    st.title("RiskRadar AI")
    st.caption("Local JSON-driven multi-agent emerging risk intelligence for reinsurance portfolios")

    with st.sidebar:
        st.header("Portfolio intake")
        with st.form("risk_form"):
            industry = st.selectbox("Department", ["Manufacturing", "Healthcare", "Retail", "Technology", "Logistics", "Other"])
            region = st.selectbox("Region", ["North America", "Europe", "APAC", "LATAM", "Global"])
            submitted = st.form_submit_button("Run RiskRadar workflow")

    if submitted:
        profile = build_profile(
            {
                "industry": industry,
                "region": region,
            }
        )
        result = run_workflow(profile)
        render_workflow(result)
    else:
        st.info("Submit the form to trigger the agent workflow and inspect the emerging risk analysis.")


if __name__ == "__main__":
    main()
