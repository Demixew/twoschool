import logging
from .db import Database

async def daily_cleanup(db: Database):
    """
    Выполняет ежедневную очистку данных, например, удаление устаревших временных изменений.
    """
    logging.info("Выполняется ежедневная очистка устаревших данных...")
    await db.clear_old_temporary_changes()
    logging.info("Очистка завершена.")