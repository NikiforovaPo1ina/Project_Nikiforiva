from backend.database.db import engine
from backend.database.models_db import Base

Base.metadata.create_all(bind=engine)

print("База данных создана")