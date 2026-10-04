from src.database.database import Database

db = Database()

db.save_upload(
    "test.csv",
    100,
    5,
    "Test Dataset"
)

print(db.get_uploads())