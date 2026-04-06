from secureflow.triage import (
    batch_related_findings,
    compute_priority_score,
    determine_escalation,
)


def test_severity_scoring():
    assert compute_priority_score({"severity": "critical"}) > compute_priority_score(
        {"severity": "high"}
    )
    assert compute_priority_score({"severity": "high"}) > compute_priority_score(
        {"severity": "medium"}
    )
    assert compute_priority_score({"severity": "medium"}) > compute_priority_score(
        {"severity": "low"}
    )


def test_standard_cwe_boost():
    base = compute_priority_score({"severity": "high", "cwe": ""})
    boosted = compute_priority_score({"severity": "high", "cwe": "CWE-89"})
    assert boosted > base


def test_escalation_auto_fix():
    assert (
        determine_escalation({"severity": "high", "cwe": "CWE-89"}) == "auto_fix"
    )
    assert (
        determine_escalation({"severity": "medium", "cwe": "CWE-79"}) == "auto_fix"
    )


def test_escalation_assist_for_critical():
    assert (
        determine_escalation({"severity": "critical", "cwe": "CWE-89"}) == "assist"
    )


def test_escalation_escalate_for_complex():
    assert (
        determine_escalation({"severity": "high", "cwe": "CWE-287"}) == "escalate"
    )
    assert (
        determine_escalation({"severity": "medium", "cwe": "CWE-362"}) == "escalate"
    )


def test_escalation_unknown_cwe():
    assert determine_escalation({"severity": "medium", "cwe": "CWE-999"}) == "assist"


def test_standard_cwe_327_and_502():
    """CWE-327 (Weak Crypto) and CWE-502 (Deserialization) should be auto-fixable."""
    assert determine_escalation({"severity": "high", "cwe": "CWE-327"}) == "auto_fix"
    assert determine_escalation({"severity": "medium", "cwe": "CWE-502"}) == "auto_fix"
    # But critical severity should go to assist
    assert determine_escalation({"severity": "critical", "cwe": "CWE-327"}) == "assist"


def test_priority_boost_for_new_standard_cwes():
    base = compute_priority_score({"severity": "high", "cwe": ""})
    assert compute_priority_score({"severity": "high", "cwe": "CWE-327"}) > base
    assert compute_priority_score({"severity": "high", "cwe": "CWE-502"}) > base


def test_batch_groups_by_file():
    findings = [
        {"file_path": "a.py", "github_alert_number": 1},
        {"file_path": "a.py", "github_alert_number": 2},
        {"file_path": "b.py", "github_alert_number": 3},
    ]
    batches = batch_related_findings(findings)
    assert len(batches) == 2
    assert len(batches[0]) == 2  # a.py group
    assert len(batches[1]) == 1  # b.py group


def test_batch_splits_large_groups():
    findings = [{"file_path": "a.py", "github_alert_number": i} for i in range(12)]
    batches = batch_related_findings(findings)
    assert len(batches) == 3  # 5 + 5 + 2
    assert len(batches[0]) == 5
    assert len(batches[2]) == 2
