from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
