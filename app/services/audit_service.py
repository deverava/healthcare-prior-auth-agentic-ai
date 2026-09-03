import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


AUDIT_FOLDER = Path("logs")
AUDIT_FOLDER.mkdir(exist_ok=True)


def write_audit_event(
    case_id: str,
    stage: str,
    event_type: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Write a PHI-minimized audit event for workflow traceability.

    Raw clinical documents, member name, and DOB should not be
    written into the general audit log.
    """

    audit_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "stage": stage,
        "event_type": event_type,
        "details": details
    }

    audit_file = AUDIT_FOLDER / f"{case_id}_audit.jsonl"

    with open(audit_file, "a", encoding="utf-8") as file:
        file.write(json.dumps(audit_event) + "\n")

    return audit_event