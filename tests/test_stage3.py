from evaluation.robustness import run_robustness_evaluation
from regulatory.control_matrix import build_control_matrix


def test_robustness_report_is_reproducible_and_scoped():
    result = run_robustness_evaluation()
    assert result["cohort_size"] == 6
    assert 0 <= result["scenario_pass_rate"] <= 1
    assert len(result["threshold_perturbations"]) == 3
    assert "not real-world ground truth" in result["evaluation_scope"]


def test_regulatory_matrix_avoids_compliance_claims():
    matrix = build_control_matrix()
    assert "not a legal opinion" in matrix["disclaimer"]
    assert any(row["framework"] == "MiCA" and row["status_rule"] == "NOT_ASSESSED" for row in matrix["controls"])
