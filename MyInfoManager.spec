# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec-файл для MyInfoManager.
Собирает всё в один EXE-файл.

Использование:
    pyinstaller MyInfoManager.spec
"""

import os
from pathlib import Path

block_cipher = None

# Пути проекта — в spec-файле используем cwd
PROJECT_ROOT = Path(os.getcwd())
SIDEBAR_BUILD = PROJECT_ROOT / "sidebar" / "build"

# Собираем все файлы из sidebar/build/
datas = []

if SIDEBAR_BUILD.exists():
    # Добавляем всю собранную статику
    for f in SIDEBAR_BUILD.rglob("*"):
        if f.is_file():
            rel = f.relative_to(SIDEBAR_BUILD)
            # PyInstaller expects: (source, dest_folder)
            datas.append((str(f), str(Path("sidebar") / "build" / rel.parent)))
else:
    print(f"WARNING: sidebar/build не найден! Фронтенд не будет включён в EXE.")
    print(f"Запустите 'cd sidebar && npm run build' перед сборкой EXE.")

a = Analysis(
    ['launcher.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # FastAPI + uvicorn
        'fastapi',
        'fastapi.applications',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.staticfiles',
        'fastapi.responses',
        'uvicorn',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.logging',
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic_core',
        # Starlette
        'starlette',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.responses',
        'starlette.staticfiles',
        'starlette.routing',
        # Python-multipart
        'multipart',
        # Наши модули (скрытые импорты)
        'db.database',
        'db.models',
        'db.migrate_tasks',
        'db.repositories',
        'db.repositories.resource_repo',
        'db.repositories.note_repo',
        'db.repositories.task_repo',
        'db.repositories.attachment_repo',
        'db.repositories.contact_repo',
        'db.repositories.settings_repo',
        'db.repositories.folder_repo',
        'db.repositories.tag_repo',
        'db.repositories.task_repo',
        'server.main',
        'server.schemas',
        'server.api',
        'server.api.resources',
        'server.api.notes',
        'server.api.tasks',
        'server.api.categories',
        'server.api.attachments',
        'server.api.settings',
        'server.api.folders_tags',
        'server.api.contacts',
        # Стандартные библиотеки которые могут быть пропущены
        'sqlite3',
        'json',
        'email.mime.text',
        'encodings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'PIL',
        'jinja2',  # не используется
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyInfoManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Показываем консоль для логов
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Можно добавить .ico файл
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyInfoManager',
)
