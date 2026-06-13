from __future__ import annotations

from pathlib import Path

from pgdbm import AsyncDatabaseManager, AsyncMigrationManager, DatabaseConfig

from atext.config import Settings


class ATextDatabase:
    """Owns the pgdbm manager for standalone atext deployments."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = AsyncDatabaseManager(DatabaseConfig(connection_string=settings.database_url, schema=None))

    async def connect(self) -> None:
        await self.db.connect()
        migrations = AsyncMigrationManager(
            self.db,
            migrations_path=str(Path(__file__).parent / "migrations"),
            module_name="atext",
        )
        await migrations.apply_pending_migrations()

    async def disconnect(self) -> None:
        await self.db.disconnect()
