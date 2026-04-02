"""
Скрипт миграции: добавляет новые поля в таблицу task и создаёт таблицу subtask.
Запускать при обновлении существующей базы данных.
"""
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "myinfo.db"


def migrate():
    """Выполнить миграцию базы данных."""
    if not DATABASE_PATH.exists():
        print(f"База данных не найдена: {DATABASE_PATH}")
        print("Сначала запустите сервер для создания БД.")
        return False

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"Подключено к базе данных: {DATABASE_PATH}")

    # Проверяем и добавляем поля в таблицу task
    cursor.execute("PRAGMA table_info(task)")
    columns = [col[1] for col in cursor.fetchall()]

    migrations_applied = False

    if 'priority' not in columns:
        print("Добавляем поле priority...")
        cursor.execute("ALTER TABLE task ADD COLUMN priority TEXT DEFAULT 'medium'")
        migrations_applied = True
    else:
        print("Поле priority уже существует")

    if 'status' not in columns:
        print("Добавляем поле status...")
        cursor.execute("ALTER TABLE task ADD COLUMN status TEXT DEFAULT 'not_done'")
        migrations_applied = True
    else:
        print("Поле status уже существует")

    if 'created_at' not in columns:
        print("Добавляем поле created_at...")
        cursor.execute("ALTER TABLE task ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        migrations_applied = True
    else:
        print("Поле created_at уже существует")

    # Создаём таблицу subtask если не существует
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subtask'")
    subtask_exists = cursor.fetchone() is not None

    if not subtask_exists:
        print("Создаём таблицу subtask...")
        cursor.execute("""
            CREATE TABLE subtask (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                due_date DATETIME,
                is_completed INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subtask_task_id
            ON subtask(task_id)
        """)
        migrations_applied = True
    else:
        print("Таблица subtask уже существует")

    conn.commit()
    conn.close()

    if migrations_applied:
        print("\n✅ Миграция успешно применена!")
    else:
        print("\n✅ Все миграции уже применены (изменений не требуется)")

    return True


if __name__ == "__main__":
    migrate()
