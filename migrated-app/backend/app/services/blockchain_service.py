"""
Blockchain service for anchoring dispute solutions.
"""
import httpx
from typing import Any, Dict, Optional

from app.core.config import settings


class BlockchainService:
    """Service for anchoring data to blockchain."""

    def __init__(self):
        self.base_url = settings.BLOCKCHAIN_API_URL
        self.username = settings.BLOCKCHAIN_USERNAME
        self.password = settings.BLOCKCHAIN_PASSWORD
        self.token: Optional[str] = None

    async def _login(self) -> bool:
        """Authenticate with blockchain API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/auth/v1/login",
                    json={
                        "username": self.username,
                        "password": self.password,
                    },
                )
                response.raise_for_status()
                data = response.json()
                self.token = data["data"]["token"]
                return True
            except Exception as e:
                print(f"Blockchain login error: {e}")
                return False

    async def anchor_data(self, owner: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Anchor data to blockchain.

        Args:
            owner: Username of data owner
            data: Data to anchor

        Returns:
            Blockchain entry ID or None if failed
        """
        if not settings.BLOCKCHAIN_ENABLED:
            return None

        try:
            # Login first
            if not await self._login():
                return None

            # Prepare request
            payload = {
                "data": {
                    "type": "entry",
                    "entry_data_hash": "hash1",
                    "owner": owner,
                    "entry_kind": "dispute_solution",
                    "entry_data": data,
                }
            }

            # Send request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/blockchain_store/v1/entries",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                response.raise_for_status()
                result = response.json()
                return result["data"]["id"]

        except Exception as e:
            print(f"Blockchain anchor error: {e}")
            return None
