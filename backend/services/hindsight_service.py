"""
Hindsight Service Implementation

Integrates with the official Hindsight memory service (via hindsight-client)
and includes an embedded local persistent memory store for zero-friction local execution.
"""

import os
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class HindsightService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        bank_id: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("HINDSIGHT_API_KEY")
        self.base_url = base_url or os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
        self.bank_id = bank_id or os.getenv("HINDSIGHT_BANK_ID", "codereview-team-memory")
        self._client = None
        self._storage_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".hindsight_memory_bank.json",
        )

    def _get_local_memories(self) -> List[Dict[str, Any]]:
        """Read local persistent memory storage."""
        if not os.path.exists(self._storage_file):
            return []
        try:
            with open(self._storage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_local_memories(self, memories: List[Dict[str, Any]]):
        """Save to local persistent memory storage."""
        with open(self._storage_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)

    def get_client(self):
        """Initialize official Hindsight client if API key is present."""
        if self._client is None and self.api_key:
            try:
                from hindsight_client import Hindsight
                self._client = Hindsight(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=30.0,
                )
            except Exception as e:
                print(f"[HindsightService] Warning: Could not initialize Hindsight cloud client: {e}")
                self._client = None
        return self._client

    async def retain_memory(self, content: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retains a new team convention or rule into Hindsight memory.
        """
        client = self.get_client()
        if client:
            try:
                response = client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    metadata=metadata,
                )
                return {
                    "bank_id": self.bank_id,
                    "content": content,
                    "status": "retained",
                    "mode": "cloud",
                    "response": response.to_dict() if hasattr(response, "to_dict") else str(response),
                }
            except Exception as e:
                print(f"[HindsightService] Cloud retain failed, falling back to local memory store: {e}")

        # Local Persistent Hindsight Bank
        memories = self._get_local_memories()
        memory_entry = {
            "bank_id": self.bank_id,
            "content": content,
            "metadata": metadata or {},
        }
        # Avoid duplicate exact content
        if not any(m.get("content") == content for m in memories):
            memories.append(memory_entry)
            self._save_local_memories(memories)

        return {
            "bank_id": self.bank_id,
            "content": content,
            "status": "retained",
            "mode": "local_persistent",
        }

    async def recall_memories(self, query: str, limit: int = 5) -> List[str]:
        """
        Recalls relevant team rules and past learnings matching the code context.
        """
        client = self.get_client()
        if client:
            try:
                recall_response = client.recall(
                    bank_id=self.bank_id,
                    query=query,
                    budget="mid",
                )
                memories = []
                if recall_response and hasattr(recall_response, "results") and recall_response.results:
                    for item in recall_response.results:
                        if hasattr(item, "text") and item.text:
                            memories.append(item.text)
                        elif isinstance(item, dict) and "text" in item:
                            memories.append(item["text"])
                if memories:
                    return memories[:limit]
            except Exception as e:
                print(f"[HindsightService] Cloud recall failed, falling back to local memory store: {e}")

        # Local Recall Strategy: Match query keywords with memory content
        memories = self._get_local_memories()
        if not memories:
            return []

        query_lower = query.lower()
        scored_memories = []
        for entry in memories:
            text = entry.get("content", "")
            # Simple keyword overlap scoring
            words = [w for w in text.lower().split() if len(w) > 3]
            score = sum(1 for w in words if w in query_lower)
            scored_memories.append((score, text))

        # Sort by relevance
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [text for score, text in scored_memories[:limit]]


hindsight_service = HindsightService()
