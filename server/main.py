"""
Точка входа веб-сервера MyInfoManager.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from db.connection import init_database
from server.api import resources, notes, tasks, categories, attachments, settings, folders_tags, contacts, auth


# Инициализация базы данных при старте
init_database()


app = FastAPI(
    title="MyInfoManager API",
    description="API для управления информационными ресурсами, заметками и задачами",
    version="1.0.0",
)

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Ограничение размера загружаемых файлов (10 MB)
app.config = {"max_upload_size": 10 * 1024 * 1024}

# Подключение роутеров API
app.include_router(resources.router)
app.include_router(notes.router)
app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(attachments.router)
app.include_router(settings.router)
app.include_router(folders_tags.router)
app.include_router(contacts.router)
app.include_router(auth.router)


@app.get("/health")
def health_check():
    """Проверка работоспособности API."""
    return {"status": "ok"}


# Раздача статических файлов фронтенда (sidebar/build/)
# Работает и в режиме разработки, и в PyInstaller
def _find_static_dir():
    """Найти директорию со статикой."""
    import sys
    # В PyInstaller файлы распакованы в _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "sidebar" / "build"
    # В режиме разработки — относительно корня проекта
    # server/main.py -> ../../sidebar/build
    return Path(__file__).parent.parent / "sidebar" / "build"

STATIC_DIR = _find_static_dir()
if STATIC_DIR.exists():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Отдаём статические файлы SPA. API роуты обрабатываются выше."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Для SPA роутинга отдаём index.html для любых неизвестных путей
        return FileResponse(STATIC_DIR / "index.html")
