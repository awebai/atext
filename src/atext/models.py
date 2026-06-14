from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateDocumentRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=160, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")
    title: str = Field(..., min_length=1, max_length=240)
    body: str = ""


class AppendVersionRequest(BaseModel):
    body: str


class DocumentSummary(BaseModel):
    document_id: UUID
    slug: str
    title: str
    current_version: int
    updated_at: datetime
    created_at: datetime


class DocumentVersion(BaseModel):
    version_id: UUID
    version_number: int
    body: str | None = None
    created_by_did_key: str
    created_by_did_aw: str | None = None
    created_by_address: str | None = None
    created_by_alias: str
    certificate_id: str
    created_at: datetime


class DocumentResponse(BaseModel):
    document_id: UUID
    slug: str
    title: str
    body: str
    current_version: int
    created_at: datetime
    updated_at: datetime
    latest: DocumentVersion


class CreatePresentationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(..., min_length=1, max_length=160, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")
    version: int | None = Field(default=None, ge=1)
    ttl_seconds: int | None = Field(default=None, ge=1)


class PresentationResponse(BaseModel):
    token: str
    url: str
    expires_at: datetime


class BillingCaps(BaseModel):
    max_documents: int | None
    max_versions_per_doc: int | None


class BillingUsage(BaseModel):
    documents: int
    max_versions_per_doc: int


class BillingResponse(BaseModel):
    team_id: str
    tier: str
    caps: BillingCaps
    usage: BillingUsage
