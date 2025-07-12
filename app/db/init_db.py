from sqlalchemy import inspect
from app.db.database import engine, Base
from app.db.models import user

def init():
    inspector = inspect(engine)

    print("cek tabel")
    existing_tables = inspector.get_table_names()

    if "users" in existing_tables:
        print("safe")
    else:
        print("membuat tabel baru")
        Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init()
