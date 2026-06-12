from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException
from pgdbm import AsyncDatabaseManager

from atext.auth import Principal
from atext.config import Settings


async def create_document(
    db: AsyncDatabaseManager,
    *,
    principal: Principal,
    slug: str,
    title: str,
    body: str,
) -> dict:
    document_id = uuid4()
    version_id = uuid4()
    try:
        async with db.transaction() as tx:
            await tx.execute(
                """
                INSERT INTO {{tables.documents}}
                  (document_id, team_id, slug, title, created_by_did_key, created_by_did_aw, created_by_alias)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                document_id,
                principal.team_id,
                slug,
                title,
                principal.did_key,
                principal.did_aw,
                principal.alias,
            )
            await tx.execute(
                """
                INSERT INTO {{tables.document_versions}}
                  (version_id, document_id, version_number, body, created_by_did_key,
                   created_by_did_aw, created_by_address, created_by_alias, certificate_id)
                VALUES ($1, $2, 1, $3, $4, $5, $6, $7, $8)
                """,
                version_id,
                document_id,
                body,
                principal.did_key,
                principal.did_aw,
                principal.address,
                principal.alias,
                principal.certificate_id,
            )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Document slug already exists for this team") from exc
        raise
    return await get_document(db, principal=principal, slug=slug)


async def get_billing_status(
    db: AsyncDatabaseManager,
    *,
    principal: Principal,
    settings: Settings,
) -> dict:
    row = await db.fetch_one(
        """
        SELECT COUNT(DISTINCT d.document_id) AS documents,
               COUNT(v.version_id) AS versions,
               COALESCE(MAX(per_doc.version_count), 0) AS max_versions_per_doc
        FROM {{tables.documents}} d
        LEFT JOIN {{tables.document_versions}} v ON v.document_id = d.document_id
        LEFT JOIN (
            SELECT document_id, COUNT(*) AS version_count
            FROM {{tables.document_versions}}
            GROUP BY document_id
        ) per_doc ON per_doc.document_id = d.document_id
        WHERE d.team_id = $1
        """,
        principal.team_id,
    )
    usage = dict(row or {})
    return {
        "tier": "free",
        "caps": {
            "max_documents": settings.free_max_documents,
            "max_versions_per_doc": settings.free_max_versions_per_doc,
        },
        "usage": {
            "documents": int(usage.get("documents") or 0),
            "versions": int(usage.get("versions") or 0),
            "max_versions_per_doc": int(usage.get("max_versions_per_doc") or 0),
        },
    }


async def list_documents(db: AsyncDatabaseManager, *, principal: Principal) -> list[dict]:
    rows = await db.fetch_all(
        """
        SELECT d.document_id, d.slug, d.title, d.created_at, d.updated_at,
               COALESCE(MAX(v.version_number), 0) AS current_version
        FROM {{tables.documents}} d
        LEFT JOIN {{tables.document_versions}} v ON v.document_id = d.document_id
        WHERE d.team_id = $1
        GROUP BY d.document_id, d.slug, d.title, d.created_at, d.updated_at
        ORDER BY d.updated_at DESC, d.slug ASC
        """,
        principal.team_id,
    )
    return [dict(row) for row in rows]


async def get_document(db: AsyncDatabaseManager, *, principal: Principal, slug: str) -> dict:
    row = await db.fetch_one(
        """
        SELECT d.document_id, d.slug, d.title, d.created_at, d.updated_at,
               v.version_id, v.version_number, v.body, v.created_by_did_key,
               v.created_by_did_aw, v.created_by_address, v.created_by_alias,
               v.certificate_id, v.created_at AS version_created_at
        FROM {{tables.documents}} d
        JOIN {{tables.document_versions}} v ON v.document_id = d.document_id
        WHERE d.team_id = $1 AND d.slug = $2
        ORDER BY v.version_number DESC
        LIMIT 1
        """,
        principal.team_id,
        slug,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")
    data = dict(row)
    return {
        "document_id": data["document_id"],
        "slug": data["slug"],
        "title": data["title"],
        "body": data["body"],
        "current_version": data["version_number"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "latest": {
            "version_id": data["version_id"],
            "version_number": data["version_number"],
            "body": data["body"],
            "created_by_did_key": data["created_by_did_key"],
            "created_by_did_aw": data["created_by_did_aw"],
            "created_by_address": data["created_by_address"],
            "created_by_alias": data["created_by_alias"],
            "certificate_id": data["certificate_id"],
            "created_at": data["version_created_at"],
        },
    }


async def append_version(
    db: AsyncDatabaseManager,
    *,
    principal: Principal,
    slug: str,
    body: str,
) -> dict:
    document = await db.fetch_one(
        "SELECT document_id FROM {{tables.documents}} WHERE team_id = $1 AND slug = $2",
        principal.team_id,
        slug,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    document_id: UUID = document["document_id"]
    version_id = uuid4()
    async with db.transaction() as tx:
        current = await tx.fetch_one(
            "SELECT COALESCE(MAX(version_number), 0) AS n FROM {{tables.document_versions}} WHERE document_id = $1",
            document_id,
        )
        next_version = int(current["n"] or 0) + 1
        await tx.execute(
            """
            INSERT INTO {{tables.document_versions}}
              (version_id, document_id, version_number, body, created_by_did_key,
               created_by_did_aw, created_by_address, created_by_alias, certificate_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            version_id,
            document_id,
            next_version,
            body,
            principal.did_key,
            principal.did_aw,
            principal.address,
            principal.alias,
            principal.certificate_id,
        )
        await tx.execute(
            "UPDATE {{tables.documents}} SET updated_at = NOW() WHERE document_id = $1",
            document_id,
        )
    return await get_document(db, principal=principal, slug=slug)


async def list_versions(db: AsyncDatabaseManager, *, principal: Principal, slug: str) -> list[dict]:
    document = await db.fetch_one(
        "SELECT document_id FROM {{tables.documents}} WHERE team_id = $1 AND slug = $2",
        principal.team_id,
        slug,
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    rows = await db.fetch_all(
        """
        SELECT version_id, version_number, NULL::TEXT AS body, created_by_did_key,
               created_by_did_aw, created_by_address, created_by_alias,
               certificate_id, created_at
        FROM {{tables.document_versions}}
        WHERE document_id = $1
        ORDER BY version_number DESC
        """,
        document["document_id"],
    )
    return [dict(row) for row in rows]
