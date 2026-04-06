FIX_GUIDANCE: dict[str, str] = {
    "CWE-89": (
        "Use parameterized queries or an ORM. Replace string interpolation/concatenation "
        "in SQL with placeholder parameters (e.g., `cursor.execute('SELECT * FROM users "
        "WHERE id = ?', (user_id,))`)."
    ),
    "CWE-79": (
        "Use proper output encoding. In Flask, use `render_template` with Jinja2 "
        "auto-escaping instead of returning raw f-string HTML. Never embed user input "
        "directly in HTML strings."
    ),
    "CWE-22": (
        "Validate and sanitize file paths. Use `os.path.realpath()` and verify the "
        "resolved path starts with the allowed base directory. Reject paths containing `..`."
    ),
    "CWE-798": (
        "Move credentials to environment variables. Use `os.environ.get('VAR_NAME')` or "
        "a config file that is .gitignored. Remove all hardcoded secrets from source."
    ),
    "CWE-78": (
        "Use `subprocess.run()` with a list of arguments instead of `shell=True` or "
        "`os.popen()`. Never pass user input directly to shell commands. Use "
        "`shlex.quote()` if shell invocation is unavoidable."
    ),
    "CWE-20": (
        "Add input validation: check types, ranges, formats, and allowed values. "
        "Reject or sanitize any input that doesn't match expected patterns before processing."
    ),
    "CWE-327": (
        "Replace weak cryptographic algorithms (MD5, SHA1, DES, RC4) with modern alternatives. "
        "Use `hashlib.sha256()` or `hashlib.sha3_256()` for hashing, and `cryptography.fernet` "
        "or AES-256-GCM for encryption. Never roll your own crypto."
    ),
    "CWE-502": (
        "Replace `pickle.loads()` / `yaml.load()` with safe alternatives. Use `json.loads()` "
        "for data interchange, `yaml.safe_load()` for YAML, or define an explicit allowlist "
        "of deserializable types. Never deserialize untrusted data with pickle."
    ),
}


def build_fix_prompt(finding: dict, repo_url: str, batch: list[dict] | None = None) -> str:
    if batch and len(batch) > 1:
        return _build_batch_prompt(batch, repo_url)
    return _build_single_prompt(finding, repo_url)


def _build_single_prompt(finding: dict, repo_url: str) -> str:
    cwe = finding.get("cwe", "")
    guidance = FIX_GUIDANCE.get(cwe, "Apply the standard remediation for this vulnerability class.")
    alert_num = finding.get("github_alert_number", 0)
    rule_id = finding.get("rule_id", "unknown")
    rule_short = rule_id.split("/")[-1] if "/" in rule_id else rule_id

    return f"""You are fixing a security vulnerability identified by GitHub CodeQL.

## Repository
{repo_url}

## Security Finding
- **Rule**: {finding.get('rule_id', '')} ({finding.get('rule_name', '')})
- **Severity**: {finding.get('severity', 'medium').upper()}
- **CWE**: {cwe}
- **File**: `{finding.get('file_path', '')}`  (lines {finding.get('start_line', '?')}-{finding.get('end_line', '?')})
- **Description**: {finding.get('description', '')}
- **GitHub Alert**: {finding.get('html_url', '')}

## Instructions
1. Clone the repository and check out a new branch named `secureflow/fix-{rule_short}-{alert_num}`
2. Navigate to `{finding.get('file_path', '')}` and understand the vulnerable code
3. Apply the **minimal, targeted fix** that resolves the vulnerability without changing functionality
4. Ensure existing tests still pass. If a test file exists, add a test for the fix.
5. Create a pull request with:
   - Title: `[SecureFlow] Fix {cwe}: {finding.get('rule_name', '')}`
   - Body explaining what the vulnerability was, what the fix does, and referencing the CodeQL alert
6. Do NOT introduce new dependencies unless absolutely necessary
7. Follow the existing code style of the repository

## Fix Guidance
{guidance}
"""


def _build_batch_prompt(batch: list[dict], repo_url: str) -> str:
    findings_text = ""
    for i, f in enumerate(batch, 1):
        findings_text += f"""
### Finding {i}
- **Rule**: {f.get('rule_id', '')} ({f.get('rule_name', '')})
- **Severity**: {f.get('severity', 'medium').upper()}
- **CWE**: {f.get('cwe', '')}
- **Location**: `{f.get('file_path', '')}` lines {f.get('start_line', '?')}-{f.get('end_line', '?')}
- **Description**: {f.get('description', '')}
"""

    file_path = batch[0].get("file_path", "unknown")
    rule_parts = {f.get("rule_id", "").split("/")[-1] for f in batch}
    branch_suffix = "-".join(sorted(rule_parts))[:60]

    return f"""You are fixing multiple security vulnerabilities in the same file, identified by GitHub CodeQL.

## Repository
{repo_url}

## Findings in `{file_path}`
{findings_text}

## Instructions
1. Clone the repository and create branch `secureflow/fix-batch-{branch_suffix}`
2. Fix ALL the listed vulnerabilities in `{file_path}`
3. Apply minimal, targeted fixes that resolve each vulnerability without changing functionality
4. Run existing tests and ensure they pass
5. Create ONE pull request covering all fixes, with a clear description of each change
6. Do NOT introduce new dependencies unless absolutely necessary
7. Follow the existing code style of the repository
"""
