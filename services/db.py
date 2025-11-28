import aiosqlite
from pathlib import Path

DB_PATH = Path("school_guide.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                chat_id INTEGER PRIMARY KEY,
                schedule_text TEXT
            )
        """)
        await db.commit()

async def save_schedule(chat_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO students (chat_id, schedule_text) VALUES (?, ?)",
            (chat_id, text)
        )
        await db.commit()

async def get_schedule(chat_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT schedule_text FROM students WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None