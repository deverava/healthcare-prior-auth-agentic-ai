import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


POLICY_FOLDER = Path("data/policies")


def load_policy_file(file_path: Path) -> Optional[Dict[str, Any]]:
    try:
        # Skip empty files
        if file_path.stat().st_size == 0:
            print(f"Skipping empty policy file: {file_path.name}")
            return None

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        print(f"Skipping invalid JSON policy file: {file_path.name}")
        return None


def is_policy_active(policy: Dict[str, Any], request_date: str) -> bool:
    request_dt = datetime.strptime(request_date, "%Y-%m-%d")
    effective_dt = datetime.strptime(policy["effective_date"], "%Y-%m-%d")
    expiration_dt = datetime.strptime(policy["expiration_date"], "%Y-%m-%d")

    return effective_dt <= request_dt <= expiration_dt


def find_matching_policy(
    product_code: str,
    procedure_code: str,
    request_date: str
) -> Optional[Dict[str, Any]]:

    for policy_file in POLICY_FOLDER.glob("*.json"):

        policy = load_policy_file(policy_file)

        if policy is None:
            continue

        product_matches = policy.get("product_code") == product_code
        procedure_matches = policy.get("procedure_code") == procedure_code
        date_matches = is_policy_active(policy, request_date)

        if product_matches and procedure_matches and date_matches:
            return policy

    return None