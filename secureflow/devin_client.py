import httpx
from typing import Optional


class DevinClient:
    def __init__(self, api_key: str, base_url: str = "https://api.devin.ai/v1"):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def create_session(
        self,
        prompt: str,
        tags: Optional[list[str]] = None,
        playbook_id: Optional[str] = None,
    ) -> dict:
        payload: dict = {"prompt": prompt}
        if tags:
            payload["tags"] = tags
        if playbook_id:
            payload["playbook_id"] = playbook_id

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/sessions",
                headers=self.headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_session(self, session_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/sessions/{session_id}",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def list_sessions(
        self, tags: Optional[list[str]] = None, limit: int = 50
    ) -> dict:
        params: dict = {"limit": limit}
        if tags:
            params["tags"] = tags

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/sessions",
                headers=self.headers,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()

    async def send_message(self, session_id: str, message: str) -> dict:
        """Send a follow-up message to an active Devin session."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/sessions/{session_id}/messages",
                headers=self.headers,
                json={"message": message},
            )
            resp.raise_for_status()
            return resp.json()

    async def create_playbook(
        self, name: str, description: str, playbook: str
    ) -> dict:
        """Create a reusable playbook for security remediation."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/playbooks",
                headers=self.headers,
                json={"name": name, "description": description, "playbook": playbook},
            )
            resp.raise_for_status()
            return resp.json()

    async def list_playbooks(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/playbooks",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def add_knowledge(self, body: str, name: str = "SecureFlow CWE Guidance") -> dict:
        """Push organizational knowledge so Devin understands CWE remediation patterns."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/knowledge",
                headers=self.headers,
                json={"body": body, "name": name, "type": "text"},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_session_insights(self, session_id: str) -> dict:
        """Retrieve AI-generated insights after session completion."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/sessions/{session_id}/insights",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def create_secret(self, name: str, value: str) -> dict:
        """Register a secret for Devin to use (e.g., GitHub token for PR creation)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/secrets",
                headers=self.headers,
                json={"name": name, "value": value},
            )
            resp.raise_for_status()
            return resp.json()
