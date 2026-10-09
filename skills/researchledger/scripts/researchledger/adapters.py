"""Offline adapter boundary; remote services are deliberately not imported."""
import json
from pathlib import Path
from typing import Protocol, Dict, Any
from .schema import fields


class EvidenceAdapter(Protocol):
    def read(self, locator: str) -> Dict[str, Any]:
        """Return observed/trials plus a source locator; never issue scientific decisions."""
        ...


class JsonEvidenceAdapter:
    """Normalize an explicitly exported local tracker report, with no network side effects."""
    def read(self, locator):
        path = Path(locator)
        raw = path.read_bytes()
        result = json.loads(raw)
        fields(result, ("observed", "trials"))
        from .store import digest
        return {"report": result, "source": {"adapter": "json", "locator": str(path), "sha256": digest(raw)}}
