"""
Тесты для модуля базы данных.
"""
import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

from db.database import init_database, create_tables
from db.models import Resource, Note, Task, KategoryResource, KategoryNote, KategoryTask, Contact, ContactGroup
from db.repositories.resource_repo import ResourceRepository
from db.repositories.note_repo import NoteRepository
from db.repositories.task_repo import TaskRepository


@pytest.fixture
def db_connection():
    """Создать временную базу данных для тестов."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    conn = init_database(db_path)
    yield conn
    conn.close()
    # Игнорируем ошибки удаления на Windows
    try:
        db_path.unlink()
    except (PermissionError, OSError):
        pass


class TestDatabaseInit:
    """Тесты инициализации базы данных."""
    
    def test_init_database(self, db_connection):
        """Тест инициализации базы данных."""
        assert db_connection is not None
        cursor = db_connection.cursor()
        
        # Проверка существования таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'kategory_resource', 'resource',
            'kategory_note', 'note',
            'kategory_task', 'task'
        }
        assert expected_tables.issubset(tables)


class TestResourceRepository:
    """Тесты репозитория ресурсов."""
    
    @pytest.fixture
    def repo(self, db_connection):
        return ResourceRepository(db_connection)
    
    def test_create_category(self, repo):
        """Тест создания категории ресурса."""
        category = repo.create_category("Сайты")
        assert category.id is not None
        assert category.name == "Сайты"
    
    def test_get_categories(self, repo):
        """Тест получения списка категорий."""
        repo.create_category("Сайты")
        repo.create_category("Документы")
        
        categories = repo.get_categories()
        assert len(categories) == 2
        assert any(c.name == "Сайты" for c in categories)
    
    def test_create_resource(self, repo):
        """Тест создания ресурса."""
        category = repo.create_category("Сайты")
        resource = Resource(
            name="Google",
            kategory_id=category.id,
            url="https://google.com",
            description="Поисковик"
        )
        created = repo.create(resource)
        
        assert created.id is not None
        assert created.name == "Google"
        assert created.kategory_id == category.id
    
    def test_get_all_resources(self, repo):
        """Тест получения всех ресурсов."""
        category = repo.create_category("Сайты")
        repo.create(Resource(name="Site1", kategory_id=category.id, url="http://site1.com"))
        repo.create(Resource(name="Site2", kategory_id=category.id, url="http://site2.com"))
        
        resources = repo.get_all()
        assert len(resources) == 2
    
    def test_get_resource_by_id(self, repo):
        """Тест получения ресурса по ID."""
        category = repo.create_category("Сайты")
        resource = repo.create(Resource(name="Google", kategory_id=category.id, url="https://google.com"))
        
        found = repo.get_by_id(resource.id)
        assert found is not None
        assert found.name == "Google"
    
    def test_search_resources(self, repo):
        """Тест поиска ресурсов."""
        category = repo.create_category("Сайты")
        repo.create(Resource(name="Google", kategory_id=category.id, url="https://google.com"))
        repo.create(Resource(name="GitHub", kategory_id=category.id, url="https://github.com"))

        results = repo.search("Git")
        assert len(results) == 1
        assert results[0].name == "GitHub"

    def test_update_resource(self, repo):
        """Тест обновления ресурса."""
        category = repo.create_category("Сайты")
        resource = repo.create(Resource(name="OldName", kategory_id=category.id, url="http://old.com"))
        
        resource.name = "NewName"
        resource.url = "http://new.com"
        updated = repo.update(resource)
        
        assert updated is not None
        assert updated.name == "NewName"
        assert updated.url == "http://new.com"
    
    def test_delete_resource(self, repo):
        """Тест удаления ресурса."""
        category = repo.create_category("Сайты")
        resource = repo.create(Resource(name="ToDelete", kategory_id=category.id))
        
        assert repo.delete(resource.id) is True
        assert repo.get_by_id(resource.id) is None
    
    def test_delete_category(self, repo):
        """Тест удаления категории."""
        category = repo.create_category("ToDelete")
        assert repo.delete_category(category.id) is True
        assert repo.get_category_by_id(category.id) is None


class TestNoteRepository:
    """Тесты репозитория заметок."""
    
    @pytest.fixture
    def repo(self, db_connection):
        return NoteRepository(db_connection)
    
    def test_create_category(self, repo):
        """Тест создания категории заметки."""
        category = repo.create_category("Личное")
        assert category.id is not None
        assert category.name == "Личное"
    
    def test_create_note(self, repo):
        """Тест создания заметки."""
        category = repo.create_category("Личное")
        note = Note(
            name="Моя заметка",
            kategory_id=category.id,
            note_text="Текст заметки",
            data_time=datetime.now()
        )
        created = repo.create(note)
        
        assert created.id is not None
        assert created.name == "Моя заметка"
    
    def test_get_all_notes(self, repo):
        """Тест получения всех заметок."""
        category = repo.create_category("Личное")
        repo.create(Note(name="Note1", kategory_id=category.id, note_text="Text1"))
        repo.create(Note(name="Note2", kategory_id=category.id, note_text="Text2"))
        
        notes = repo.get_all()
        assert len(notes) == 2
    
    def test_search_notes(self, repo):
        """Тест поиска заметок."""
        category = repo.create_category("Личное")
        repo.create(Note(name="Встреча", kategory_id=category.id, note_text="Обсудить проект"))
        repo.create(Note(name="Покупки", kategory_id=category.id, note_text="Купить хлеб"))
        
        results = repo.search("проект")
        assert len(results) == 1
        assert results[0].name == "Встреча"
    
    def test_update_note(self, repo):
        """Тест обновления заметки."""
        category = repo.create_category("Личное")
        note = repo.create(Note(name="Old", kategory_id=category.id, note_text="Old text"))
        
        note.name = "Updated"
        note.note_text = "New text"
        updated = repo.update(note)
        
        assert updated is not None
        assert updated.name == "Updated"
    
    def test_delete_note(self, repo):
        """Тест удаления заметки."""
        category = repo.create_category("Личное")
        note = repo.create(Note(name="ToDelete", kategory_id=category.id))
        
        assert repo.delete(note.id) is True
        assert repo.get_by_id(note.id) is None


class TestTaskRepository:
    """Тесты репозитория задач."""
    
    @pytest.fixture
    def repo(self, db_connection):
        return TaskRepository(db_connection)
    
    def test_create_category(self, repo):
        """Тест создания категории задачи."""
        category = repo.create_category("Работа")
        assert category.id is not None
        assert category.name == "Работа"
    
    def test_create_task(self, repo):
        """Тест создания задачи."""
        category = repo.create_category("Работа")
        task = Task(
            name="Сделать отчёт",
            kategory_id=category.id,
            description="Подготовить ежемесячный отчёт",
            data_time=datetime.now()
        )
        created = repo.create(task)
        
        assert created.id is not None
        assert created.name == "Сделать отчёт"
    
    def test_get_all_tasks(self, repo):
        """Тест получения всех задач."""
        category = repo.create_category("Работа")
        repo.create(Task(name="Task1", kategory_id=category.id))
        repo.create(Task(name="Task2", kategory_id=category.id))
        
        tasks = repo.get_all()
        assert len(tasks) == 2
    
    def test_search_tasks(self, repo):
        """Тест поиска задач."""
        category = repo.create_category("Работа")
        repo.create(Task(name="Созвон", kategory_id=category.id, description="Обсудить с командой"))
        repo.create(Task(name="Код ревью", kategory_id=category.id, description="Проверить PR"))
        
        results = repo.search("командой")
        assert len(results) == 1
        assert results[0].name == "Созвон"
    
    def test_update_task(self, repo):
        """Тест обновления задачи."""
        category = repo.create_category("Работа")
        task = repo.create(Task(name="Old", kategory_id=category.id, description="Old desc"))
        
        task.name = "Updated"
        task.description = "New description"
        updated = repo.update(task)
        
        assert updated is not None
        assert updated.name == "Updated"
    
    def test_delete_task(self, repo):
        """Тест удаления задачи."""
        category = repo.create_category("Работа")
        task = repo.create(Task(name="ToDelete", kategory_id=category.id))

        assert repo.delete(task.id) is True
        assert repo.get_by_id(task.id) is None


class TestContactRepository:
    """Тесты репозитория контактов."""

    @pytest.fixture
    def repo(self, db_connection):
        from db.repositories.contact_repo import ContactRepository
        return ContactRepository(db_connection)

    def test_create_group(self, repo):
        """Тест создания группы контактов."""
        group = repo.create_group("ТестСемья123", "#FF6B6B")
        assert group.id is not None
        assert group.name == "ТестСемья123"
        assert group.color == "#FF6B6B"

    def test_get_groups(self, repo):
        """Тест получения списка групп."""
        repo.create_group("ТестГруппаА123", "#FF0000")
        repo.create_group("ТестГруппаБ123", "#00FF00")

        groups = repo.get_groups()
        assert len(groups) >= 2

    def test_create_contact(self, repo):
        """Тест создания контакта."""
        group = repo.create_group("ТестКоллеги123")
        contact = Contact(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            group_id=group.id,
            company="ООО Ромашка",
            position="Менеджер",
            is_favorite=False
        )
        created = repo.create(contact)

        assert created.id is not None
        assert created.first_name == "Иван"
        assert created.last_name == "Иванов"
        assert created.group_name == "ТестКоллеги123"

    def test_get_all_contacts(self, repo):
        """Тест получения всех контактов."""
        repo.create(Contact(first_name="Петр", last_name="Петров"))
        repo.create(Contact(first_name="Анна", last_name="Анна"))

        contacts = repo.get_all()
        assert len(contacts) == 2

    def test_search_contacts(self, repo):
        """Тест поиска контактов."""
        repo.create(Contact(first_name="Алексей", last_name="Смирнов"))
        repo.create(Contact(first_name="Дмитрий", last_name="Кузнецов"))

        results = repo.search("Смирнов")
        assert len(results) == 1
        assert results[0].last_name == "Смирнов"

    def test_update_contact(self, repo):
        """Тест обновления контакта."""
        contact = repo.create(Contact(first_name="Тест", last_name="Тестов"))

        contact.first_name = "Обновлённый"
        contact.company = "Новая компания"
        updated = repo.update(contact)

        assert updated is not None
        assert updated.first_name == "Обновлённый"
        assert updated.company == "Новая компания"

    def test_delete_contact(self, repo):
        """Тест удаления контакта."""
        contact = repo.create(Contact(first_name="НаУдаление", last_name="Удалов"))

        assert repo.delete(contact.id) is True
        assert repo.get_by_id(contact.id) is None

    def test_toggle_favorite(self, repo):
        """Тест переключения избранного."""
        contact = repo.create(Contact(first_name="Избранный", last_name="Избранов", is_favorite=False))

        toggled = repo.toggle_favorite(contact.id)
        assert toggled.is_favorite == True

        toggled = repo.toggle_favorite(contact.id)
        assert toggled.is_favorite == False

    def test_delete_group(self, repo):
        """Тест удаления группы."""
        group = repo.create_group("ТестГруппа")

        assert repo.delete_group(group.id) is True
        assert repo.get_group_by_id(group.id) is None
