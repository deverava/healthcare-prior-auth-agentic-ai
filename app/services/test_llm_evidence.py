import json
from pathlib import Path

from app.services.policy_service import (
    find_matching_policy,
)

from app.services.llm_service import (
    extract_clinical_evidence_with_llm,
)


def main():
    case_file = Path(
        "data/cases/happy_path.json"
    )

    with open(
        case_file,
        "r",
        encoding="utf-8",
    ) as file:
        case = json.load(file)

    policy = find_matching_policy(
        product_code=case[
            "insurance"
        ]["product_code"],
        procedure_code=case[
            "requested_service"
        ]["procedure_code"],
        request_date=case[
            "request_date"
        ],
    )

    if policy is None:
        print("No matching policy found.")
        return

    evidence = (
        extract_clinical_evidence_with_llm(
            case=case,
            policy=policy,
        )
    )

    print(
        json.dumps(
            evidence,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()