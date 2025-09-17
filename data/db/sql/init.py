import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect
from data.db.sql.client import engine, Base
from data.db.sql import models

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  

    async with engine.begin() as conn:
        def do_inspect(sync_conn):
            inspector = inspect(sync_conn)
            existing_tables = inspector.get_table_names()
            return existing_tables

        existing_tables = await conn.run_sync(do_inspect)

    print("Tables in DB:", existing_tables)
    print("Tables in models.py:", Base.metadata.tables.keys())

    missing = set(Base.metadata.tables.keys()) - set(existing_tables)
    if missing:
        print("⚠️ Masih ada tabel hilang:", missing)
    else:
        print("✅ Semua tabel aman")

if __name__ == "__main__":
    asyncio.run(init())
