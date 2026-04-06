import httpx
from typing import Optional


class GitHubCodeQLClient:
    def __init__(self, token: str, owner: str, repo: str):
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_open_alerts(self, severity: Optional[str] = None) -> list[dict]:
        params: dict = {"state": "open", "per_page": 100}
        if severity:
            params["severity"] = severity

        alerts: list[dict] = []
        page = 1

        async with httpx.AsyncClient() as client:
            while True:
                params["page"] = page
                resp = await client.get(
                    f"{self.base_url}/code-scanning/alerts",
                    headers=self.headers,
                    params=params,
                )
                resp.raise_for_status()
                batch = resp.json()
                if not batch:
                    break
                alerts.extend(batch)
                if len(batch) < 100:
                    break
                page += 1

        return alerts

    def normalize_alert(self, alert: dict) -> dict:
        rule = alert.get("rule", {})
        instance = alert.get("most_recent_instance", {})
        location = instance.get("location", {})

        return {
            "github_alert_number": alert["number"],
            "rule_id": rule.get("id", ""),
            "rule_name": rule.get("name", rule.get("id", "")),
            "severity": rule.get("security_severity_level", "medium"),
            "cwe": self._extract_cwe(rule.get("tags", [])),
            "description": rule.get("full_description", rule.get("description", "")),
            "file_path": location.get("path", ""),
            "start_line": location.get("start_line", 0),
            "end_line": location.get("end_line", 0),
            "html_url": alert.get("html_url", ""),
        }

    @staticmethod
    def _extract_cwe(tags: list[str]) -> str:
        for tag in tags:
            if tag.startswith("external/cwe/cwe-"):
                num = tag.replace("external/cwe/cwe-", "")
                return f"CWE-{num}"
        return ""
