"""
Тесты для API сервера.
"""
import pytest
from fastapi.testclient import TestClient
import tempfile
from pathlib import Path
import sqlite3

from server.main import app
from db.database import get_connection, init_database, DATABASE_PATH


@pytest.fixture
def client():
    """Создать тестовый клиент API."""
    # Используем временную базу данных для тестов
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    # Переопределяем путь к БД
    import db.database
    db.database.DATABASE_PATH = db_path
    
    # Инициализируем БД
    init_database(db_path)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Удаляем файл (игнорируем ошибки на Windows)
    try:
        db_path.unlink()
    except (PermissionError, OSError):
        pass  # Файл может быть заблокирован на Windows


class TestRootEndpoints:
    """Тесты корневых эндпоинтов."""
    
    def test_root(self, client):
        """Тест корневого эндпоинта."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "MyInfoManager API"
        assert "docs" in data
    
    def test_health(self, client):
        """Тест проверки работоспособности."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestResourceAPI:
    """Тесты API ресурсов."""
    
    def test_create_category(self, client):
        """Тест создания категории ресурса."""
        response = client.post("/api/resources/categories?name=Сайты")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Сайты"
        assert "id" in data
    
    def test_get_categories(self, client):
        """Тест получения списка категорий."""
        client.post("/api/resources/categories?name=Категория1")
        client.post("/api/resources/categories?name=Категория2")
        
        response = client.get("/api/resources/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_create_resource(self, client):
        """Тест создания ресурса."""
        # Создаём категорию
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        # Создаём ресурс
        response = client.post(
            "/api/resources",
            json={
                "name": "Google",
                "kategory_id": category_id,
                "url": "https://google.com",
                "description": "Поисковик"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Google"
        assert "id" in data
    
    def test_get_resources(self, client):
        """Тест получения списка ресурсов."""
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        client.post("/api/resources", json={"name": "Site1", "kategory_id": category_id, "url": "http://site1.com"})
        client.post("/api/resources", json={"name": "Site2", "kategory_id": category_id, "url": "http://site2.com"})
        
        response = client.get("/api/resources")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_resource_by_id(self, client):
        """Тест получения ресурса по ID."""
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        create_response = client.post(
            "/api/resources",
            json={"name": "Google", "kategory_id": category_id, "url": "https://google.com"}
        )
        resource_id = create_response.json()["id"]
        
        response = client.get(f"/api/resources/{resource_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Google"
    
    def test_get_resource_not_found(self, client):
        """Тест получения несуществующего ресурса."""
        response = client.get("/api/resources/9999")
        assert response.status_code == 404
    
    def test_update_resource(self, client):
        """Тест обновления ресурса."""
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        create_response = client.post(
            "/api/resources",
            json={"name": "OldName", "kategory_id": category_id, "url": "http://old.com"}
        )
        resource_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/resources/{resource_id}",
            json={"name": "NewName", "kategory_id": category_id, "url": "http://new.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NewName"
    
    def test_delete_resource(self, client):
        """Тест удаления ресурса."""
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        create_response = client.post(
            "/api/resources",
            json={"name": "ToDelete", "kategory_id": category_id}
        )
        resource_id = create_response.json()["id"]
        
        response = client.delete(f"/api/resources/{resource_id}")
        assert response.status_code == 200
        
        # Проверяем, что ресурс удалён
        get_response = client.get(f"/api/resources/{resource_id}")
        assert get_response.status_code == 404
    
    def test_search_resources(self, client):
        """Тест поиска ресурсов."""
        cat_response = client.post("/api/resources/categories?name=Сайты")
        category_id = cat_response.json()["id"]
        
        client.post("/api/resources", json={"name": "Google", "kategory_id": category_id})
        client.post("/api/resources", json={"name": "GitHub", "kategory_id": category_id})
        
        response = client.get("/api/resources/search?q=Git")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "GitHub"


class TestNoteAPI:
    """Тесты API заметок."""
    
    def test_create_note(self, client):
        """Тест создания заметки."""
        response = client.post(
            "/api/notes",
            json={
                "name": "Моя заметка",
                "kategory_id": None,
                "note_text": "Текст заметки"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Моя заметка"
        assert "id" in data
    
    def test_get_notes(self, client):
        """Тест получения списка заметок."""
        client.post("/api/notes", json={"name": "Note1", "note_text": "Text1"})
        client.post("/api/notes", json={"name": "Note2", "note_text": "Text2"})
        
        response = client.get("/api/notes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_search_notes(self, client):
        """Тест поиска заметок."""
        client.post("/api/notes", json={"name": "Встреча", "note_text": "Обсудить проект"})
        client.post("/api/notes", json={"name": "Покупки", "note_text": "Купить хлеб"})
        
        response = client.get("/api/notes/search?q=проект")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestTaskAPI:
    """Тесты API задач."""
    
    def test_create_task(self, client):
        """Тест создания задачи."""
        response = client.post(
            "/api/tasks",
            json={
                "name": "Сделать отчёт",
                "kategory_id": None,
                "description": "Подготовить ежемесячный отчёт"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Сделать отчёт"
        assert "id" in data
    
    def test_get_tasks(self, client):
        """Тест получения списка задач."""
        client.post("/api/tasks", json={"name": "Task1", "description": "Desc1"})
        client.post("/api/tasks", json={"name": "Task2", "description": "Desc2"})
        
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_search_tasks(self, client):
        """Тест поиска задач."""
        client.post("/api/tasks", json={"name": "Созвон", "description": "Обсудить с командой"})
        client.post("/api/tasks", json={"name": "Код ревью", "description": "Проверить PR"})
        
        response = client.get("/api/tasks/search?q=командой")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestContactAPI:
    """Тесты API контактов."""

    def test_create_group(self, client):
        """Тест создания группы контактов."""
        response = client.post("/api/contacts/groups", json={"name": "ТестГруппа123", "color": "#FF6B6B"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ТестГруппа123"
        assert data["color"] == "#FF6B6B"
        assert "id" in data

    def test_get_groups(self, client):
        """Тест получения списка групп."""
        client.post("/api/contacts/groups", json={"name": "ТестГруппаА", "color": "#FF0000"})
        client.post("/api/contacts/groups", json={"name": "ТестГруппаБ", "color": "#00FF00"})

        response = client.get("/api/contacts/groups")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_create_contact(self, client):
        """Тест создания контакта."""
        # Создаём группу с уникальным именем
        group_response = client.post("/api/contacts/groups", json={"name": "ТестКоллеги123", "color": "#008888"})
        group_id = group_response.json()["id"]

        response = client.post("/api/contacts", json={
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "group_id": group_id,
            "company": "ООО Ромашка",
            "position": "Менеджер",
            "is_favorite": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Иван"
        assert data["last_name"] == "Иванов"
        assert data["group_name"] == "ТестКоллеги123"
        assert "id" in data

    def test_get_contacts(self, client):
        """Тест получения списка контактов."""
        client.post("/api/contacts", json={
            "first_name": "Петр",
            "last_name": "Петров",
            "middle_name": "Петрович"
        })
        client.post("/api/contacts", json={
            "first_name": "Анна",
            "last_name": "Анна",
            "middle_name": "Анновна"
        })

        response = client.get("/api/contacts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_search_contacts(self, client):
        """Тест поиска контактов."""
        client.post("/api/contacts", json={
            "first_name": "Алексей",
            "last_name": "Смирнов",
            "middle_name": "Алексеевич"
        })
        client.post("/api/contacts", json={
            "first_name": "Дмитрий",
            "last_name": "Кузнецов",
            "middle_name": "Дмитриевич"
        })

        response = client.get("/api/contacts/search?q=Смирнов")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["last_name"] == "Смирнов"

    def test_update_contact(self, client):
        """Тест обновления контакта."""
        # Создаём контакт
        create_response = client.post("/api/contacts", json={
            "first_name": "Тест",
            "last_name": "Тестов",
            "middle_name": "Тестович"
        })
        contact_id = create_response.json()["id"]

        # Обновляем
        response = client.put(f"/api/contacts/{contact_id}", json={
            "first_name": "Обновлённый",
            "company": "Новая компания"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Обновлённый"
        assert data["company"] == "Новая компания"

    def test_delete_contact(self, client):
        """Тест удаления контакта."""
        # Создаём контакт
        create_response = client.post("/api/contacts", json={
            "first_name": "НаУдаление",
            "last_name": "Удалов"
        })
        contact_id = create_response.json()["id"]

        # Удаляем
        response = client.delete(f"/api/contacts/{contact_id}")
        assert response.status_code == 200

        # Проверяем что удалён
        get_response = client.get(f"/api/contacts/{contact_id}")
        assert get_response.status_code == 404

    def test_toggle_favorite(self, client):
        """Тест переключения избранного."""
        # Создаём контакт
        create_response = client.post("/api/contacts", json={
            "first_name": "Избранный",
            "last_name": "Избранов",
            "is_favorite": False
        })
        contact_id = create_response.json()["id"]

        # Переключаем
        response = client.post(f"/api/contacts/{contact_id}/toggle-favorite")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] == True

        # Переключаем обратно
        response = client.post(f"/api/contacts/{contact_id}/toggle-favorite")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] == False


class TestCategoryAPI:
    """Тесты API категорий."""
    
    def test_get_all_categories(self, client):
        """Тест получения всех категорий."""
        # Создаём категории разных типов
        client.post("/api/resources/categories?name=Ресурс1")
        client.post("/api/notes/categories?name=Заметка1")
        client.post("/api/tasks/categories?name=Задача1")
        
        response = client.get("/api/categories/resources")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        response = client.get("/api/categories/notes")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        response = client.get("/api/categories/tasks")
        assert response.status_code == 200
        assert len(response.json()) == 1
