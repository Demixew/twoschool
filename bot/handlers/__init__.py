from aiogram import Router

from . import ask_schedule, schedule_upload, secret_commands, start, common_requests
from ..export import get_export_router, create_schedule_ics_file


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(schedule_upload.router)
    router.include_router(secret_commands.router)
    router.include_router(common_requests.router)
    router.include_router(ask_schedule.router)
    return router