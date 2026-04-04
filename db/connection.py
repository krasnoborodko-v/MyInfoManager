"""
Абстрактный слой базы данных — поддержка SQLite и PostgreSQL.

Переключение через переменные окружения:
    DATABASE_TYPE=sqlite   — локальный режим (файл myinfo.db)
    DATABASE_TYPE=postgres — режим сервера (PostgreSQL)

Для PostgreSQL также нужны:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""
import os
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional


class Row(ABC):
    """Абстрактная строка результата (dict-like)."""

    @abstractmethod
    def __getitem__(self, key): ...

    @abstractmethod
    def keys(self): ...

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default


class Cursor(ABC):
    """Абстрактный курсор БД."""

    @abstractmethod
    def execute(self, sql: str, parameters: tuple = ...): ...

    @abstractmethod
    def executemany(self, sql: str, seq_of_parameters: list): ...

    @abstractmethod
    def fetchone(self) -> Optional[Row]: ...

    @abstractmethod
    def fetchall(self) -> List[Row]: ...

    @abstractmethod
    def fetchmany(self, size: int) -> List[Row]: ...

    @property
    @abstractmethod
    def lastrowid(self) -> Optional[int]: ...

    @property
    @abstractmethod
    def rowcount(self) -> int: ...

    @abstractmethod
    def description(self): ...


class Connection(ABC):
    """Абстрактное соединение с БД."""

    @abstractmethod
    def cursor(self) -> Cursor: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @contextmanager
    def transaction(self):
        """Контекстный менеджер транзакции."""
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise


# ============================================================
# SQLite реализация
# ============================================================

class _SQLiteRow(Row):
    def __init__(self, row: sqlite3.Row):
        self._row = row

    def __getitem__(self, key):
        return self._row[key]

    def keys(self):
        return self._row.keys()


class _SQLiteCursor(Cursor):
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def execute(self, sql: str, parameters: tuple = ()):
        self._cursor.execute(sql, parameters)
        return self

    def executemany(self, sql: str, seq_of_parameters: list):
        self._cursor.executemany(sql, seq_of_parameters)
        return self

    def fetchone(self) -> Optional[Row]:
        row = self._cursor.fetchone()
        return _SQLiteRow(row) if row else None

    def fetchall(self) -> List[Row]:
        return [_SQLiteRow(r) for r in self._cursor.fetchall()]

    def fetchmany(self, size: int) -> List[Row]:
        return [_SQLiteRow(r) for r in self._cursor.fetchmany(size)]

    @property
    def lastrowid(self) -> Optional[int]:
        return self._cursor.lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def description(self):
        return self._cursor.description


class _SQLiteConnection(Connection):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def cursor(self) -> Cursor:
        c = self._conn.cursor()
        c.row_factory = sqlite3.Row
        return _SQLiteCursor(c)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    @property
    def isolation_level(self):
        return self._conn.isolation_level


# ============================================================
# PostgreSQL реализация (через psycopg2 — sync)
# ============================================================

class _PostgresRow(Row):
    def __init__(self, row, description=None):
        self._row = row
        self._desc = description

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        # dict-like access по имени колонки
        if self._desc:
            for i, col in enumerate(self._desc):
                if col[0] == key:
                    return self._row[i]
        raise KeyError(key)

    def keys(self):
        if self._desc:
            return [col[0] for col in self._desc]
        return []


class _PostgresCursor(Cursor):
    def __init__(self, conn):
        self._conn = conn
        self._cur = None
        self._desc = None

    def execute(self, sql: str, parameters: tuple = ()):
        self._cur = self._conn.cursor()
        # Заменяем ? на %s для psycopg2
        adapted_sql = sql.replace("?", "%s")
        self._cur.execute(adapted_sql, parameters)
        self._desc = self._cur.description
        return self

    def executemany(self, sql: str, seq_of_parameters: list):
        self._cur = self._conn.cursor()
        adapted_sql = sql.replace("?", "%s")
        self._cur.executemany(adapted_sql, seq_of_parameters)
        self._desc = self._cur.description
        return self

    def fetchone(self) -> Optional[Row]:
        if not self._cur:
            return None
        row = self._cur.fetchone()
        return _PostgresRow(row, self._desc) if row else None

    def fetchall(self) -> List[Row]:
        if not self._cur:
            return []
        return [_PostgresRow(r, self._desc) for r in self._cur.fetchall()]

    def fetchmany(self, size: int) -> List[Row]:
        if not self._cur:
            return []
        return [_PostgresRow(r, self._desc) for r in self._cur.fetchmany(size)]

    @property
    def lastrowid(self) -> Optional[int]:
        if not self._cur:
            return None
        # psycopg: lastrowid работает только для INSERT ... RETURNING
        # Для совместимости — пробуем
        try:
            return self._cur.lastrowid
        except AttributeError:
            return None

    @property
    def rowcount(self) -> int:
        if not self._cur:
            return 0
        return self._cur.rowcount

    def description(self):
        return self._desc


class _PostgresConnection(Connection):
    def __init__(self, conn):
        self._conn = conn

    def cursor(self) -> Cursor:
        return _PostgresCursor(self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


# ============================================================
# Фабрика — создаёт нужный тип соединения
# ============================================================

def _get_db_type() -> str:
    """Определить тип БД из окружения."""
    return os.environ.get("DATABASE_TYPE", "sqlite").lower()


def _create_sqlite(db_path: Optional[Path] = None) -> Connection:
    """Создать SQLite соединение."""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "data" / "myinfo.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    return _SQLiteConnection(conn)


def _create_postgres() -> Connection:
    """Создать PostgreSQL соединение."""
    import psycopg2

    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "myinfomanager"),
        user=os.environ.get("POSTGRES_USER", "myinfo"),
        password=os.environ.get("POSTGRES_PASSWORD", "myinfo"),
    )
    conn.autocommit = False
    return _PostgresConnection(conn)


def get_connection(db_path: Optional[Path] = None) -> Connection:
    """
    Получить подключение к БД (SQLite или PostgreSQL).

    Args:
        db_path: Путь к SQLite файлу (игнорируется для PostgreSQL)
    """
    db_type = _get_db_type()
    if db_type == "postgres":
        return _create_postgres()
    else:
        return _create_sqlite(db_path)


def create_tables(conn: Connection) -> None:
    """
    Создать все таблицы. SQL одинаковый для SQLite и PostgreSQL
    (с синтаксисом ? вместо %s — обёртка сама конвертирует).
    """
    cursor = conn.cursor()

    # Таблица категорий ресурсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategory_resource (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Таблица ресурсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Таблица заметок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            kategory_id INTEGER,
            note_text TEXT,
            data_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            folder_id INTEGER,
            FOREIGN KEY (kategory_id) REFERENCES kategory_note(id) ON DELETE SET NULL,
            FOREIGN KEY (folder_id) REFERENCES folder(id) ON DELETE SET NULL
        )
    """)

    # Миграция folder_id (только SQLite — для PostgreSQL создаётся сразу)
    if _get_db_type() == "sqlite":
        cursor.execute("PRAGMA table_info(note)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'folder_id' not in columns:
            cursor.execute("ALTER TABLE note ADD COLUMN folder_id INTEGER")

    # Таблица категорий задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategory_task (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Таблица задач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            kategory_id INTEGER,
            description TEXT,
            data_time TIMESTAMP,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'not_done',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kategory_id) REFERENCES kategory_task(id) ON DELETE SET NULL
        )
    """)

    # Миграции (только SQLite)
    if _get_db_type() == "sqlite":
        cursor.execute("PRAGMA table_info(task)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'priority' not in columns:
            cursor.execute("ALTER TABLE task ADD COLUMN priority TEXT DEFAULT 'medium'")
        if 'status' not in columns:
            cursor.execute("ALTER TABLE task ADD COLUMN status TEXT DEFAULT 'not_done'")
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE task ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # Таблица подзадач
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtask (
            id SERIAL PRIMARY KEY,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TIMESTAMP,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subtask_task_id ON subtask(task_id)
    """)

    # Миграция description для subtask (SQLite)
    if _get_db_type() == "sqlite":
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subtask'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(subtask)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'description' not in columns:
                cursor.execute("ALTER TABLE subtask ADD COLUMN description TEXT")

    # Таблица вложений
    if _get_db_type() == "sqlite":
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachment'")
        attachment_exists = cursor.fetchone() is not None
    else:
        # PostgreSQL: проверяем через information_schema
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'attachment'
            )
        """)
        row = cursor.fetchone()
        attachment_exists = row[0] if row else False

    if not attachment_exists:
        cursor.execute("""
            CREATE TABLE attachment (
                id SERIAL PRIMARY KEY,
                note_id INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                file_data BYTEA NOT NULL,
                file_size INTEGER,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
            )
        """)
    else:
        if _get_db_type() == "sqlite":
            cursor.execute("PRAGMA table_info(attachment)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'note' not in columns:
                cursor.execute("ALTER TABLE attachment ADD COLUMN note TEXT")
            if 'file_type' not in columns:
                cursor.execute("ALTER TABLE attachment ADD COLUMN file_type TEXT DEFAULT 'application/octet-stream'")

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attachment_note_id ON attachment(note_id)
    """)

    # Таблица настроек
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Настройки по умолчанию
    if _get_db_type() == "sqlite":
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES
                ('audio_limit', '5', 'Максимальное количество аудиофайлов в заметке'),
                ('image_quality', '80', 'Качество сжатия изображений (0-100)'),
                ('theme', 'dark', 'Тема оформления')
        """)
    else:
        cursor.execute("""
            INSERT INTO settings (key, value, description)
            VALUES
                ('audio_limit', '5', 'Максимальное количество аудиофайлов в заметке'),
                ('image_quality', '80', 'Качество сжатия изображений (0-100)'),
                ('theme', 'dark', 'Тема оформления')
            ON CONFLICT (key) DO NOTHING
        """)

    # Таблица папок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folder (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            parent_id INTEGER,
            note_category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folder(id) ON DELETE CASCADE,
            FOREIGN KEY (note_category_id) REFERENCES kategory_note(id) ON DELETE CASCADE
        )
    """)

    # Таблица тегов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#008888',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Связующая таблица заметки-теги
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_tag (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
        )
    """)

    # Индексы
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

    # === Контакты ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_group (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#008888',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact (
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL DEFAULT '',
            last_name TEXT NOT NULL DEFAULT '',
            middle_name TEXT DEFAULT '',
            group_id INTEGER,
            phones TEXT,
            emails TEXT,
            address TEXT,
            company TEXT,
            position TEXT,
            birth_date TIMESTAMP,
            photo BYTEA,
            photo_type TEXT,
            socials TEXT,
            website TEXT,
            is_favorite INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES contact_group(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_group ON contact(group_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_favorite ON contact(is_favorite)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_contact_name ON contact(last_name, first_name)
    """)

    # Начальные группы
    cursor.execute("SELECT COUNT(*) FROM contact_group")
    row = cursor.fetchone()
    count = row[0] if row else 0
    if count == 0:
        default_groups = [
            ('Семья', '#FF6B6B'),
            ('Родственники', '#FFA07A'),
            ('Друзья', '#4ECDC4'),
            ('Коллеги', '#45B7D1'),
            ('Знакомые', '#96CEB4'),
            ('Соседи', '#FFEAA7'),
            ('Клиенты', '#DDA0DD'),
            ('Партнёры', '#98D8C8'),
            ('Другое', '#888889'),
        ]
        cursor.executemany(
            "INSERT INTO contact_group (name, color) VALUES (?, ?)",
            default_groups
        )

    conn.commit()


def init_database(db_path: Optional[Path] = None) -> Connection:
    """
    Инициализировать БД: подключиться и создать таблицы.

    Returns:
        Connection — абстрактное соединение (SQLite или PostgreSQL)
    """
    conn = get_connection(db_path)
    create_tables(conn)
    return conn


if __name__ == "__main__":
    db_type = _get_db_type()
    conn = init_database()
    print(f"БД инициализирована: тип={db_type}")
    conn.close()
