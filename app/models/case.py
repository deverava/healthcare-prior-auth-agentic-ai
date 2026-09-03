from typing import List
from pydantic import BaseModel


class Member(BaseModel):
    member_id: str
    name: str
    date_of_birth: str


class Provider(BaseModel):
    provider_id: str
    name: str
    specialty: str


class Insurance(BaseModel):
    payer: str
    plan_name: str
    product_code: str
    coverage_effective_date: str


class RequestedService(BaseModel):
    procedure_name: str
    procedure_code: str
    diagnosis: str
    diagnosis_code: str
    body_site: str


class ClinicalDocument(BaseModel):
    document_id: str
    document_type: str
    document_date: str
    content: str


class PriorAuthorizationCase(BaseModel):
    case_id: str
    request_date: str
    urgency: str
    member: Member
    provider: Provider
    insurance: Insurance
    requested_service: RequestedService
    clinical_documents: List[ClinicalDocument]