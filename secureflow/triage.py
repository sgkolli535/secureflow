from secureflow.models import EscalationLevel

SEVERITY_SCORES: dict[str, float] = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
}

# CWEs with well-known, standard fixes — good candidates for auto-fix
STANDARD_FIX_CWES: set[str] = {
    "CWE-89",   # SQL Injection → parameterized queries
    "CWE-79",   # XSS → output encoding / template escaping
    "CWE-22",   # Path Traversal → path validation
    "CWE-798",  # Hardcoded Credentials → env vars
    "CWE-78",   # Command Injection → subprocess with list args
    "CWE-20",   # Input Validation → add validation
    "CWE-327",  # Weak Crypto → use modern algorithm
    "CWE-502",  # Deserialization → safe deserialization
}

# CWEs that require architectural changes — escalate to humans
COMPLEX_CWES: set[str] = {
    "CWE-287",  # Authentication issues
    "CWE-306",  # Missing auth for critical function
    "CWE-362",  # Race conditions
    "CWE-269",  # Privilege escalation
    "CWE-918",  # SSRF (context-dependent)
}


def compute_priority_score(finding: dict) -> float:
    severity = finding.get("severity", "medium")
    base = SEVERITY_SCORES.get(severity, 0.5)

    # Boost for standard-fix CWEs — we know Devin can handle these
    cwe = finding.get("cwe", "")
    if cwe in STANDARD_FIX_CWES:
        base = min(base * 1.15, 1.0)

    # Slight penalty for complex CWEs (still high priority, but deprioritised for automation)
    if cwe in COMPLEX_CWES:
        base *= 0.9

    return round(base, 3)


def determine_escalation(finding: dict) -> str:
    cwe = finding.get("cwe", "")
    severity = finding.get("severity", "medium")

    # Complex CWEs always escalate
    if cwe in COMPLEX_CWES:
        return EscalationLevel.ESCALATE.value

    # Standard CWEs: auto-fix unless critical severity
    if cwe in STANDARD_FIX_CWES:
        if severity == "critical":
            return EscalationLevel.ASSIST.value
        return EscalationLevel.AUTO_FIX.value

    # Unknown CWE patterns → assist mode (Devin tries, human reviews)
    return EscalationLevel.ASSIST.value


def batch_related_findings(findings: list[dict]) -> list[list[dict]]:
    """Group findings by file_path so Devin can fix multiple issues per session."""
    by_file: dict[str, list[dict]] = {}
    for f in findings:
        path = f.get("file_path", "unknown")
        by_file.setdefault(path, []).append(f)

    batches: list[list[dict]] = []
    for group in by_file.values():
        for i in range(0, len(group), 5):
            batches.append(group[i : i + 5])

    return batches
