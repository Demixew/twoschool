import aiosqlite
from pathlib import Path
from datetime import date

class Database:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    chat_id INTEGER PRIMARY KEY,
                    schedule_text TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS temporary_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    change_description TEXT NOT NULL,
                    change_date DATE NOT NULL
                )
            """)
            await db.commit()

    async def save_schedule(self, chat_id: int, text: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO students (chat_id, schedule_text) VALUES (?, ?)",
                (chat_id, text)
            )
            await db.commit()

    async def get_schedule(self, chat_id: int) -> str | None:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT schedule_text FROM students WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def get_all_chat_ids(self) -> list[int]:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT chat_id FROM students WHERE schedule_text IS NOT NULL") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def add_temporary_change(self, chat_id: int, description: str):
        today = date.today()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO temporary_changes (chat_id, change_description, change_date) VALUES (?, ?, ?)",
                (chat_id, description, today)
            )
            await db.commit()

    async def get_temporary_changes_for_today(self, chat_id: int) -> list[str]:
        today = date.today()
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT change_description FROM temporary_changes WHERE chat_id = ? AND change_date = ?", (chat_id, today)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def clear_old_temporary_changes(self):
        """Удаляет все временные изменения, которые старше сегодняшнего дня."""
        today = date.today()
        async with aiosqlite.connect(self.path) as db:
            # Удаляем записи, где дата строго меньше сегодняшней
            await db.execute("DELETE FROM temporary_changes WHERE change_date < ?", (today,))
            await db.commit()