"""
Точка входа веб-сервера MyInfoManager.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_database
from server.api import resources, notes, tasks, categories, attachments, settings, folders_tags


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
    allow_origins=["*"],  # В продакшене указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(resources.router)
app.include_router(notes.router)
app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(attachments.router)
app.include_router(settings.router)
app.include_router(folders_tags.router)


@app.get("/")
def root():
    """Корневой эндпоинт."""
    return {
        "message": "MyInfoManager API",
        "docs": "/docs",
        "endpoints": {
            "resources": "/api/resources",
            "notes": "/api/notes",
            "tasks": "/api/tasks",
            "categories": "/api/categories",
        }
    }


@app.get("/health")
def health_check():
    """Проверка работоспособности API."""
    return {"status": "ok"}
