from sqlalchemy import inspect
from app.db.sql.client import engine, Base
from app.db.sql import models

def init():
    inspector = inspect(engine)

    existing_tables = inspector.get_table_names()
    print("Tables in DB:", existing_tables)

    defined_tables = Base.metadata.tables.keys()
    print("Tables in models.py:", defined_tables)

    missing = set(defined_tables) - set(existing_tables)
    if missing:
        print("Create new tables:", missing)
        Base.metadata.create_all(bind=engine)
    else:
        print("All tabel safe")

if __name__ == "__main__":
    init()