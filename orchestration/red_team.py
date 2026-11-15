"""Sequential orchestration of the five specialist agents."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from html import unescape
import re
import time
from orchestration.report_generator import generate_report

REPORT_DIR = Path("reports")


def clean_text(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not isinstance(text, str):
        return str(text)

    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def write_markdown(report: dict) -> str:
    REPORT_DIR.mkdir(exist_ok=True)

    output_file = REPORT_DIR / "red_team_report.md"

    lines = []

    def add(text=""):
        lines.append(text)

    risk = report["final_risk"]

    # ==========================================================
    # HEADER
    # ==========================================================

    add("# 🛡️ Agentic Red Team Assessment Report")
    add()
    add(f"**Project:** {report['project']}")
    add(f"**Generated:** {report['generated_at']}")
    add(f"**Scope:** {report['scope']}")
    add()
    add("---")
    add()

    # ==========================================================
    # EXECUTIVE SUMMARY
    # ==========================================================

    add("# Executive Summary")
    add()

    add(
        f"**Overall Risk Score:** "
        f"**{risk['score']:.3f}/1.0 ({risk['severity']})**"
    )

    add()
    add("## Risk Formula")
    add()

    add(f"`{risk['formula']}`")
    add()

    add("## Risk Factors")
    add()

    for name, value in risk["factors"].items():
        add(f"- **{name.replace('_',' ').title()}**: {value}")

    add()

    # ==========================================================
    # RECONNAISSANCE
    # ==========================================================

    recon = report["agents"]["1_reconnaissance"]

    evidence = recon["evidence"]

    add("# 1. Reconnaissance")
    add()

    add("## Asset Inventory")
    add()
    add(f"- Target: {evidence['target']}")
    add(f"- Base URL: {clean_text(evidence['base_url'])}")
    add(f"- Sample Transactions: {evidence['sample_transaction_count']}")
    add(f"- Sample Alerts: {evidence['sample_alert_count']}")
    add(f"- Sample Audit Events: {evidence['sample_audit_event_count']}")
    add()

    # Health

    health = evidence["health"]

    add("## Health Status")
    add()

    add("| Property | Value |")
    add("|----------|----------|")
    add(f"| Status | {health['status']} |")
    add(f"| Service | {health['service']} |")
    add(f"| Timestamp | {health['timestamp']} |")

    add()

    # Endpoints

    add("## Endpoint Inventory")
    add()

    add("| Method | Endpoint | Summary | Operation ID |")
    add("|----------|----------|----------|----------|")

    for ep in evidence["endpoints"]:
        add(
            f"| {ep['method']} "
            f"| `{ep['path']}` "
            f"| {ep['summary']} "
            f"| {ep['operation_id']} |"
        )

    add()

    # Dependencies

    add("## Technology Stack")
    add()

    for dep in evidence["observed_dependencies"]:
        add(f"- {dep}")

    add()

    # Limitations

    add("## Reconnaissance Limitations")
    add()

    for item in evidence["limitations"]:
        add(f"- {item}")

    add()

    # Analysis

    add("## Reconnaissance Agent Analysis")
    add()
    add(recon["analysis"])
    add()

    # ==========================================================
    # ATTACK SIMULATION
    # ==========================================================

    attacker = report["agents"]["2_attacker"]

    add("# 2. Attack Simulation")
    add()

    add(f"**Scenario:** {attacker['evidence']['scenario']}")
    add()
    add(f"**Scope:** {attacker['evidence']['scope']}")
    add()

    for test in attacker["evidence"]["tests"]:

        add(f"## Test: {test['name']}")
        add()

        add(f"- HTTP Status: {test.get('http_status')}")
        add()

        if "accepted" in test:
            add(f"- Accepted: {test['accepted']}")

        if "rejected_as_expected" in test:
            add(f"- Rejected As Expected: {test['rejected_as_expected']}")

        if "authorization_header_sent" in test:
            add(
                f"- Authorization Header Sent: "
                f"{test['authorization_header_sent']}"
            )

        add()

        if "response" in test:

            tx = test["response"]["transaction"]

            add("### Transaction Details")
            add()

            add("| Field | Value |")
            add("|----------|----------|")

            for k, v in tx.items():
                add(f"| {k} | {v} |")

            add()

            add("### Detection Explanation")
            add()

            for exp in test["response"]["explanation"]:
                add(f"- {clean_text(exp)}")

            add()

            add(
                f"**Decision:** "
                f"{test['response']['decision']}"
            )

            add()

        if "interpretation" in test:
            add(f"> {test['interpretation']}")
            add()

    add("## Attacker Agent Analysis")
    add()
    add(attacker["analysis"])
    add()

    # ==========================================================
    # AI ADVERSARY
    # ==========================================================

    ai = report["agents"]["3_ai_adversary"]

    add("# 3. AI Adversary Testing")
    add()

    add(f"**Scenario:** {ai['evidence']['scenario']}")
    add()
    add(f"**Scope:** {ai['evidence']['scope']}")
    add()

    for test in ai["evidence"]["tests"]:

        add(f"## {test['test']}")
        add()

        baseline = test["baseline"]
        perturbed = test["perturbed"]

        add("| Metric | Baseline | Perturbed |")
        add("|----------|----------|----------|")

        add(
            f"| Risk Score | "
            f"{baseline['risk_score']} | "
            f"{perturbed['risk_score']} |"
        )

        add(
            f"| Classification | "
            f"{baseline['classification']} | "
            f"{perturbed['classification']} |"
        )

        add(
            f"| Anomaly Score | "
            f"{baseline['anomaly_score']} | "
            f"{perturbed['anomaly_score']} |"
        )

        add()

        add(f"- Risk Score Delta: {test['risk_score_delta']}")
        add(
            f"- Classification Changed: "
            f"{test['classification_changed']}"
        )

        add()

        add("### Baseline Explanation")
        add()

        for e in baseline["explanation"]:
            add(f"- {clean_text(e)}")

        add()

        add("### Perturbed Explanation")
        add()

        for e in perturbed["explanation"]:
            add(f"- {clean_text(e)}")

        add()

    add("### Interpretation Note")
    add()
    add(ai["evidence"]["interpretation_note"])
    add()

    add("## AI Adversary Analysis")
    add()
    add(ai["analysis"])
    add()

    # ==========================================================
    # COMPLIANCE
    # ==========================================================

    compliance = report["agents"]["4_compliance_breaker"]

    add("# 4. Compliance Assessment")
    add()

    add(
        f"**Scope:** "
        f"{compliance['evidence']['assessment_scope']}"
    )

    add()

    add("## Control Review")
    add()

    for control in compliance["evidence"]["controls"]:

        add(
            f"### {control['framework']} - "
            f"{control['control']}"
        )

        add()
        add(f"**Status:** {control['status']}")
        add()
        add("**Evidence:**")
        add()
        add(control["evidence"])
        add()

    # add("## Areas Not Tested")
    # add()

    # for item in compliance["evidence"]["not_tested"]:
    #     add(f"- {item}")

    # add()

    add("## Compliance Agent Analysis")
    add()
    add(compliance["analysis"])
    add()

    # ==========================================================
    # RISK SCORING
    # ==========================================================

    risk_agent = report["agents"]["5_impact_risk_scoring"]

    add("# 5. Impact & Risk Scoring")
    add()

    add(f"**Final Score:** {risk['score']}")
    add()
    add(f"**Severity:** {risk['severity']}")
    add()
    add(f"**Scale:** {risk['scale']}")
    add()

    add("## Scoring Formula")
    add()

    add("```text" )
    add(risk["formula"])
    add("```")

    add()

    add("## Factor Breakdown")
    add()

    add("| Factor | Value |")
    add("|----------|----------|")

    for factor, value in risk["factors"].items():
        add(f"| {factor} | {value} |")

    add()

    add("## Prioritized Findings")
    add()

    for finding in risk["findings"]:

        add(
            f"### {finding['id']} - "
            f"{finding['title']}"
        )

        add()

        add(f"**Priority:** {finding['priority']}")
        add()
        add(f"**Evidence:** {finding['evidence']}")
        add()
        add("**Remediation:**")
        add()
        add(finding["remediation"])
        add()

    add("## Risk Scoring Analysis")
    add()
    add(risk_agent["analysis"])
    add()

    # ==========================================================
    # LIMITATIONS
    # ==========================================================

    add("# Assessment Limitations")
    add()

    for limitation in risk["limitations"]:
        add(f"- {limitation}")

    add()

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    add("# Final Recommendations")
    add()

    for finding in risk["findings"]:
        add(
            f"- [{finding['priority']}] "
            f"{finding['remediation']}"
        )

    add()

    # ==========================================================
    # CONCLUSION
    # ==========================================================

    add("# Conclusion")
    add()

    add(
        f"The Agentic Red Team assessment produced "
        f"a final risk score of "
        f"**{risk['score']:.3f} ({risk['severity']})**."
    )

    add()

    add(
        "The assessment identified observations related "
        "to API exposure, model sensitivity, compliance "
        "governance, and authentication controls. "
        "Additional verification is recommended before "
        "any production deployment."
    )

    add()

    output_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return str(output_file)
  

def run_red_team(use_llm: bool = True) -> dict:
    """Execute the controlled workflow. With use_llm=False, collect deterministic evidence only."""
    # Import agents lazily so --simulate-only works without provider credentials.
    from agents.reconnaissance import collect_attack_surface
    from agents.attacker import run_conventional_simulation
    from agents.ai_adversary import run_perturbation_tests
    from agents.compliance_breaker import build_compliance_evidence
    from agents.risk_scoring import calculate_risk

    from evaluation.robustness import run_robustness_evaluation
    from regulatory.control_matrix import build_control_matrix

    trace: list[dict] = []
    inputs_from = {
        "2_attacker": ["1_reconnaissance"],
        "3_ai_adversary": ["1_reconnaissance"],
        "4_compliance_breaker": ["1_reconnaissance", "2_attacker", "3_ai_adversary"],
        "5_impact_risk_scoring": ["2_attacker", "3_ai_adversary", "4_compliance_breaker"],
    }

    def step(name, fn):
        """Run one step and record when it ran, how long it took and which steps fed it."""
        started = datetime.now(timezone.utc)
        t0 = time.perf_counter()
        status = "ok"
        try:
            return fn()
        except Exception:
            status = "error"
            raise
        finally:
            trace.append({
                "step": name,
                "started_at": started.isoformat(timespec="seconds"),
                "duration_ms": round((time.perf_counter() - t0) * 1000),
                "status": status,
                "inputs_from": inputs_from.get(name, []),
            })

    recon_evidence = step("1_reconnaissance", collect_attack_surface)
    attacker_evidence = step("2_attacker", run_conventional_simulation)
    ai_evidence = step("3_ai_adversary", run_perturbation_tests)

    if use_llm:
        recon = {"evidence": recon_evidence}
        from agents.runtime import run_text
        from agents.reconnaissance import get_agent as get_recon_agent
        from agents.attacker import get_agent as get_attacker_agent
        from agents.ai_adversary import get_agent as get_ai_agent
        from agents.compliance_breaker import get_agent as get_compliance_agent
        from agents.risk_scoring import get_agent as get_risk_agent

        recon["analysis"] = run_text(get_recon_agent(), f"Analyze this observed ARMS inventory:\n{recon_evidence}")
        attacker = {"evidence": attacker_evidence, "analysis": run_text(get_attacker_agent(), f"Assess this controlled conventional security test:\n{attacker_evidence}")}
        ai = {"evidence": ai_evidence, "analysis": run_text(get_ai_agent(), f"Analyze these controlled AI input-perturbation results:\n{ai_evidence}")}
        compliance_evidence = step("4_compliance_breaker", lambda: build_compliance_evidence(recon, attacker, ai))
        compliance = {"evidence": compliance_evidence, "analysis": run_text(get_compliance_agent(), f"Assess these control observations and test results:\n{compliance_evidence}")}
        risk_evidence = step("5_impact_risk_scoring", lambda: calculate_risk(attacker, ai, compliance))
        risk = {"evidence": risk_evidence, "analysis": run_text(get_risk_agent(), f"Explain and prioritize this computed risk assessment without changing its score:\n{risk_evidence}")}
    else:
        recon = {"evidence": recon_evidence, "analysis": "LLM analysis skipped (--simulate-only)."}
        attacker = {"evidence": attacker_evidence, "analysis": "LLM analysis skipped (--simulate-only)."}
        ai = {"evidence": ai_evidence, "analysis": "LLM analysis skipped (--simulate-only)."}
        compliance_evidence = step("4_compliance_breaker", lambda: build_compliance_evidence(recon, attacker, ai))
        compliance = {"evidence": compliance_evidence, "analysis": "LLM analysis skipped (--simulate-only)."}
        risk_evidence = step("5_impact_risk_scoring", lambda: calculate_risk(attacker, ai, compliance))
        risk = {"evidence": risk_evidence, "analysis": "LLM analysis skipped (--simulate-only)."}

    stage_evidence = {
        "robustness": run_robustness_evaluation(),
        "regulatory_matrix": build_control_matrix(),
        "scenario_catalog": "scenarios/stage3_scenarios.json",
    }
    report = {
        "project": "Agentic Red Team - ARMS simulator",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Local simulator only; synthetic transactions only.",
        "agents": {
            "1_reconnaissance": recon,
            "2_attacker": attacker,
            "3_ai_adversary": ai,
            "4_compliance_breaker": compliance,
            "5_impact_risk_scoring": risk,
        },
        "final_risk": risk_evidence,
        "stage": stage_evidence,
    }
    # Information the agents cannot observe (architecture, MiCA scope, owners, deadlines).
    ctx_path = Path("config/project_context.json")
    context = json.loads(ctx_path.read_text(encoding="utf-8")) if ctx_path.exists() else {}
    undocumented = [
        f"{item.get('finding_id', section)}.{k}"
        for section, value in context.items() if section != "_comment"
        for item in (value if isinstance(value, list) else [value]) if isinstance(item, dict)
        for k, v in item.items() if v is None
    ]
    report["manual_context"] = {**context, "undocumented_fields": undocumented or "none"}
    report["interaction_log"] = trace
    REPORT_DIR.mkdir(exist_ok=True)
    output = REPORT_DIR / "red_team_report.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    markdown_file = write_markdown(report)
    
    pdf_output = output.parent / "rapport_final.pdf"

    generate_report(
        json_path=output,
        output_path=pdf_output
    )
    report["report_file"] = str(output)
    report["markdown_file"] = markdown_file
    report["pdf_file"] = str(pdf_output)

    return report
 

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local ARMS Red Team simulation")
    parser.add_argument("--simulate-only", action="store_true", help="Run API tests and deterministic scoring without calling an LLM")
    args = parser.parse_args()
    result = run_red_team(use_llm=not args.simulate_only)
    print(json.dumps({
        "report_file": result["report_file"],
        "markdown_report": result["markdown_file"],
        "pdf_file":result["pdf_file"],
        "risk_score": result["final_risk"]["score"],
        "severity": result["final_risk"]["severity"],
    }, indent=2))


if __name__ == "__main__":
    main()