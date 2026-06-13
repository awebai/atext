from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pgdbm import AsyncDatabaseManager

from atext import billing
from atext.auth import AWIDTeamCache, Principal, authenticate_request
from atext.config import Settings, get_settings
from atext.db import ATextDatabase
from atext.models import (
    BillingCheckoutResponse,
    BillingPortalResponse,
    BillingResponse,
    CreateDocumentRequest,
    DocumentResponse,
    DocumentSummary,
    DocumentVersion,
)
from atext.repository import (
    append_version,
    create_document,
    get_billing_status,
    get_document,
    list_documents,
    list_versions,
)


def create_app(settings: Settings | None = None, billing_provider: billing.BillingProvider | None = None) -> FastAPI:
    resolved = settings or get_settings()
    holder: dict[str, object] = {}

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        database = ATextDatabase(resolved)
        await database.connect()
        holder["db"] = database
        holder["team_cache"] = AWIDTeamCache(
            registry_url=resolved.awid_registry_url,
            ttl_seconds=resolved.auth_cache_ttl_seconds,
        )
        if billing_provider is not None:
            holder["billing_provider"] = billing_provider
        elif billing.checkout_configured(resolved):
            holder["billing_provider"] = billing.provider_for_settings(resolved)
        try:
            yield
        finally:
            await database.disconnect()

    app = FastAPI(title="atext", version="0.1.0", lifespan=lifespan)

    def db() -> AsyncDatabaseManager:
        database = holder.get("db")
        if not isinstance(database, ATextDatabase):
            raise RuntimeError("atext database is not initialized")
        return database.db

    def team_cache() -> AWIDTeamCache:
        cache = holder.get("team_cache")
        if not isinstance(cache, AWIDTeamCache):
            raise RuntimeError("atext auth cache is not initialized")
        return cache

    def configured_billing_provider() -> billing.BillingProvider:
        provider = holder.get("billing_provider")
        if provider is None or not billing.checkout_configured(resolved):
            raise HTTPException(status_code=503, detail=billing.billing_not_available_detail())
        return provider  # type: ignore[return-value]

    async def principal(
        request: Request,
        database: Annotated[AsyncDatabaseManager, Depends(db)],
        cache: Annotated[AWIDTeamCache, Depends(team_cache)],
    ) -> Principal:
        return await authenticate_request(request, settings=resolved, team_cache=cache, db=database)

    @app.get("/health")
    @app.get("/live")
    @app.get("/ready")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "atext"}

    @app.post("/v1/documents", response_model=DocumentResponse)
    async def create_document_route(
        request: Request,
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> dict:
        payload = CreateDocumentRequest.model_validate(await request.json())
        return await create_document(
            database,
            principal=actor,
            settings=resolved,
            slug=payload.slug,
            title=payload.title,
            body=payload.body,
        )

    @app.get("/v1/documents", response_model=list[DocumentSummary])
    async def list_documents_route(
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> list[dict]:
        return await list_documents(database, principal=actor)

    @app.get("/v1/documents/{slug}", response_model=DocumentResponse)
    async def get_document_route(
        slug: str,
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> dict:
        return await get_document(database, principal=actor, slug=slug)

    @app.post("/v1/documents/{slug}/versions", response_model=DocumentResponse)
    async def append_version_route(
        slug: str,
        request: Request,
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> dict:
        try:
            body = (await request.body()).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Version body must be valid UTF-8") from exc
        return await append_version(database, principal=actor, settings=resolved, slug=slug, body=body)

    @app.get("/v1/billing", response_model=BillingResponse)
    async def billing_route(
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> dict:
        return await get_billing_status(database, principal=actor, settings=resolved)

    @app.post("/v1/billing/checkout", response_model=BillingCheckoutResponse)
    async def checkout_route(
        actor: Annotated[Principal, Depends(principal)],
        provider: Annotated[billing.BillingProvider, Depends(configured_billing_provider)],
    ) -> dict[str, str]:
        url = await provider.checkout_url(team_id=actor.team_id, settings=resolved)
        return {"checkout_url": url}

    @app.post("/v1/billing/portal", response_model=BillingPortalResponse)
    async def portal_route(
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
        provider: Annotated[billing.BillingProvider, Depends(configured_billing_provider)],
    ) -> dict[str, str]:
        row = await database.fetch_one(
            "SELECT stripe_customer_id FROM {{tables.subscriptions}} WHERE team_id = $1",
            actor.team_id,
        )
        customer_id = str(row["stripe_customer_id"] or "") if row is not None else ""
        if not customer_id:
            raise HTTPException(
                status_code=409,
                detail={"code": "billing_portal_unavailable", "message": "No Stripe customer exists for this team."},
            )
        url = await provider.portal_url(customer_id=customer_id, settings=resolved)
        return {"portal_url": url}

    @app.post("/v1/stripe/webhook")
    async def stripe_webhook_route(
        request: Request,
        database: Annotated[AsyncDatabaseManager, Depends(db)],
        stripe_signature: Annotated[str | None, Header(alias="stripe-signature")] = None,
    ) -> dict[str, bool]:
        if not billing.webhook_configured(resolved):
            raise HTTPException(status_code=503, detail=billing.billing_not_available_detail())
        payload = await request.body()
        event = billing.parse_signed_event(payload, stripe_signature or "", str(resolved.stripe_webhook_secret))
        await billing.handle_stripe_event(database, event)
        return {"received": True}

    @app.get("/v1/documents/{slug}/versions", response_model=list[DocumentVersion])
    async def list_versions_route(
        slug: str,
        actor: Annotated[Principal, Depends(principal)],
        database: Annotated[AsyncDatabaseManager, Depends(db)],
    ) -> list[dict]:
        return await list_versions(database, principal=actor, slug=slug)

    return app


app = create_app()
