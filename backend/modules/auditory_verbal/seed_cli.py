#!/usr/bin/env python
"""
CLI wrapper for database seeding and management.

Usage:
  python seed_cli.py seed      # Seeds database with academic sample data
  python seed_cli.py reset     # Truncates all assessment data tables
  python seed_cli.py reseed    # Resets and re-seeds database
"""
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_cli")


async def run_seed():
    from app.infrastructure.persistence.database.engine import engine
    from app.infrastructure.persistence.database.session import AsyncSessionLocal
    from app.infrastructure.persistence.database.seed_data import seed_academic_dataset
    from app.infrastructure.persistence.models.orm_models import Base

    logger.info("Ensuring database tables exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Initializing database session for seeding...")
    async with AsyncSessionLocal() as db:
        await seed_academic_dataset(db)
    logger.info("Seeding completed successfully.")


async def run_reset():
    from sqlalchemy import text
    from app.infrastructure.persistence.database.session import AsyncSessionLocal

    logger.info("Resetting assessment database tables...")
    tables = [
        "assessment_reports",
        "assessment_scores",
        "construct_evaluations",
        "behavioral_evidences",
        "transcripts",
        "assessment_sessions",
        "research_snapshots",
        "prompt_audits",
        "platform_events",
    ]
    async with AsyncSessionLocal() as db:
        for t in tables:
            try:
                await db.execute(text(f"TRUNCATE TABLE {t} CASCADE;"))
                logger.info(f"Truncated table: {t}")
            except Exception as e:
                logger.warning(f"Could not truncate {t}: {e}")
        await db.commit()
    logger.info("Database reset complete.")


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "seed":
        await run_seed()
    elif cmd == "reset":
        await run_reset()
    elif cmd == "reseed":
        await run_reset()
        await run_seed()
    else:
        print(f"Unknown command: '{cmd}'. Supported commands: seed, reset, reseed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
