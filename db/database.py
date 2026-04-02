"""
Модуль подключения к базе данных и создания таблиц.
"""
import sqlite3
from pathlib import Path
from typing import Optional


DATABASE_PATH = Path(__file__).parent.parent / "data" / "myinfo.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Получить подключение к базе данных SQLite.
    
    Args:
        db_path: Путь к файлу базы данных. Если None, используется путь по умолчанию.
    
    Returns:
        Подключение к базе данных.
    """
    if db_path is None:
        db_path = DATABASE_PATH
    
    # Создаём директорию для БД, если она не существует
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Возвращаем строки как словари
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """
    Создать все необходимые таблицы в базе данных.
    
    Args:
        conn: Подключение к базе данных.
    """
    cursor = conn.cursor()
    
    # Таблица категорий ресурсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategory_resource (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Таблица ресурсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kategory_id INTEGER,
            url TEXT,
            description TEXT,
            FOREIGN KEY (kategory_id) REFERENCES kategory_resource(id) ON DELETE SET NULL
        )
    """)
    
    # Таблица категорий заметок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategory_note (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Таблица заметок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kategory_id INTEGER,
            note_text TEXT,
            data_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            folder_id INTEGER,
            FOREIGN KEY (kategory_id) REFERENCES kategory_note(id) ON DELETE SET NULL,
            FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE SET NULL
        )
    """)
    
    # Миграция: добавляем folder_id если нет
    cursor.execute("PRAGMA table_info(note)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'folder_id' not in columns:
        cursor.execute("ALTER TABLE note ADD COLUMN folder_id INTEGER")
    
    # Таблица категорий задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategory_task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Таблица задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kategory_id INTEGER,
            description TEXT,
            data_time DATETIME,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'not_done',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kategory_id) REFERENCES kategory_task(id) ON DELETE SET NULL
        )
    """)

    # Миграция: добавляем новые поля если нет
    cursor.execute("PRAGMA table_info(task)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'priority' not in columns:
        cursor.execute("ALTER TABLE task ADD COLUMN priority TEXT DEFAULT 'medium'")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE task ADD COLUMN status TEXT DEFAULT 'not_done'")
    if 'created_at' not in columns:
        cursor.execute("ALTER TABLE task ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")

    # Таблица подзадач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtask (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATETIME,
            is_completed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
        )
    """)

    # Индекс для быстрого поиска подзадач по задаче
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subtask_task_id
        ON subtask(task_id)
    """)

    # Проверяем, существует ли таблица subtask и добавляем колонку description если нужно
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subtask'")
    subtask_exists = cursor.fetchone() is not None
    
    if subtask_exists:
        cursor.execute("PRAGMA table_info(subtask)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'description' not in columns:
            cursor.execute("ALTER TABLE subtask ADD COLUMN description TEXT")

    # Таблица вложений (изображения, аудио для заметок)
    # Сначала проверяем, существует ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachment'")
    attachment_exists = cursor.fetchone() is not None
    
    if not attachment_exists:
        # Создаём новую таблицу
        cursor.execute("""
            CREATE TABLE attachment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                file_data BLOB NOT NULL,
                file_size INTEGER,
                note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
            )
        """)
    else:
        # Проверяем колонки и добавляем недостающие
        cursor.execute("PRAGMA table_info(attachment)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'note' not in columns:
            cursor.execute("ALTER TABLE attachment ADD COLUMN note TEXT")
        if 'file_type' not in columns:
            # Старая таблица имеет file_name, нужно создать новую
            # Для простоты просто добавляем file_type
            cursor.execute("ALTER TABLE attachment ADD COLUMN file_type TEXT DEFAULT 'application/octet-stream'")
    
    # Индекс для быстрого поиска вложений по заметке
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attachment_note_id
        ON attachment(note_id)
    """)

    # Таблица настроек
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Добавляем настройки по умолчанию
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value, description)
        VALUES 
            ('audio_limit', '5', 'Максимальное количество аудиофайлов в заметке'),
            ('image_quality', '80', 'Качество сжатия изображений (0-100)'),
            ('theme', 'dark', 'Тема оформления')
    """)

    # Таблица папок для заметок (иерархическая структура)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            note_category_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folder(id) ON DELETE CASCADE,
            FOREIGN KEY (note_category_id) REFERENCES kategory_note(id) ON DELETE CASCADE
        )
    """)

    # Таблица тегов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#008888',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Связующая таблица заметки-теги (многие-ко-многим)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_tag (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
        )
    """)

    # Индексы для быстрого поиска
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_folder_parent ON folder(parent_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_folder_category ON folder(note_category_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_tag_note ON note_tag(note_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_tag_tag ON note_tag(tag_id)
    """)

    # === Таблицы для контактов ===

    # Таблица групп контактов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_group (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#008888',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица контактов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL DEFAULT '',
            last_name TEXT NOT NULL DEFAULT '',
            middle_name TEXT DEFAULT '',
            group_id INTEGER,
            phones TEXT,
            emails TEXT,
            address TEXT,
            company TEXT,
            position TEXT,
            birth_date DATETIME,
            photo BLOB,
            photo_type TEXT,
            socials TEXT,
            website TEXT,
            is_favorite INTEGER DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES contact_group(id) ON DELETE SET NULL
        )
    """)

    # Индексы для контактов
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_group ON contact(group_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_favorite ON contact(is_favorite)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_name ON contact(last_name, first_name)
    """)

    # Добавляем начальные группы контактов, если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM contact_group")
    if cursor.fetchone()[0] == 0:
        default_groups = [
            ('Семья', '#FF6B6B'),
            ('Родственники', '#FFA07A'),
            ('Друзья', '#4ECDC4'),
            ('Коллеги', '#45B7D1'),
            ('Знакомые', '#96CEB4'),
            ('Соседи', '#FFEAA7'),
            ('Клиенты', '#DDA0DD'),
            ('Партнёры', '#98D8C8'),
            ('Другое', '#888888'),
        ]
        cursor.executemany(
            "INSERT INTO contact_group (name, color) VALUES (?, ?)",
            default_groups
        )

    conn.commit()


def init_database(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Инициализировать базу данных: подключиться и создать таблицы.
    
    Args:
        db_path: Путь к файлу базы данных. Если None, используется путь по умолчанию.
    
    Returns:
        Подключение к базе данных.
    """
    conn = get_connection(db_path)
    create_tables(conn)
    return conn


if __name__ == "__main__":
    # Тестовый запуск
    conn = init_database()
    print(f"База данных успешно инициализирована: {DATABASE_PATH}")
    conn.close()
