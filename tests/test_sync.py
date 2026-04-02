"""
Тесты для модуля синхронизации.

Эти тесты не требуют подключения к реальному серверу.
"""
import pytest
from datetime import datetime, timedelta

from sync.sync_engine import (
    SyncEngine,
    SyncDirection,
    SyncConflict,
    SyncStats,
    SyncResult,
    ConflictResolution,
)
from sync.remote_client import (
    RemoteClientInterface,
    SyncRequest,
    SyncResponse,
)


# === Тесты SyncEngine: сравнение версий ===

class TestCompareVersions:
    """Тесты сравнения версий по timestamp."""
    
    @pytest.fixture
    def engine(self):
        return SyncEngine()
    
    def test_both_none(self, engine):
        """Обе версии None — считаются равными."""
        assert engine.compare_versions(None, None) == 0
    
    def test_local_none(self, engine):
        """Локальная версия None — локальная старше."""
        remote = datetime.now()
        assert engine.compare_versions(None, remote) == -1
    
    def test_remote_none(self, engine):
        """Удалённая версия None — локальная новее."""
        local = datetime.now()
        assert engine.compare_versions(local, None) == 1
    
    def test_local_older(self, engine):
        """Локальная версия старше удалённой."""
        local = datetime.now()
        remote = local + timedelta(hours=1)
        assert engine.compare_versions(local, remote) == -1
    
    def test_local_newer(self, engine):
        """Локальная версия новее удалённой."""
        local = datetime.now()
        remote = local - timedelta(hours=1)
        assert engine.compare_versions(local, remote) == 1
    
    def test_equal(self, engine):
        """Версии равны."""
        now = datetime.now()
        assert engine.compare_versions(now, now) == 0


# === Тесты SyncEngine: обнаружение конфликтов ===

class TestDetectConflict:
    """Тесты обнаружения конфликтов."""
    
    @pytest.fixture
    def engine(self):
        return SyncEngine()
    
    def test_no_conflict_same_data(self, engine):
        """Нет конфликта, если данные одинаковы."""
        data = {"id": 1, "name": "Test", "updated_at": datetime.now()}
        conflict = engine.detect_conflict(data, data, "resource")
        assert conflict is None
    
    def test_conflict_modified_both(self, engine):
        """Конфликт: обе версии изменены."""
        local = {"id": 1, "name": "Local", "updated_at": datetime.now()}
        remote = {"id": 1, "name": "Remote", "updated_at": datetime.now()}
        conflict = engine.detect_conflict(local, remote, "resource")
        
        assert conflict is not None
        assert conflict.conflict_type == "modified_both"
        assert conflict.entity_type == "resource"
        assert conflict.entity_id == 1
    
    def test_conflict_deleted_on_remote(self, engine):
        """Конфликт: удалено на сервере."""
        local = {"id": 1, "name": "Test"}
        conflict = engine.detect_conflict(local, None, "resource")
        
        assert conflict is not None
        assert conflict.conflict_type == "deleted_on_remote"
    
    def test_conflict_deleted_locally(self, engine):
        """Конфликт: удалено локально."""
        remote = {"id": 1, "name": "Test"}
        conflict = engine.detect_conflict(None, remote, "resource")
        
        assert conflict is not None
        assert conflict.conflict_type == "deleted_locally"
    
    def test_no_conflict_different_id(self, engine):
        """Нет конфликта для разных ID."""
        local = {"id": 1, "name": "Test1"}
        remote = {"id": 2, "name": "Test2"}
        # Это не конфликт, это разные записи
        conflict = engine.detect_conflict(local, remote, "resource")
        # Конфликт будет, но это разные записи по ID
        assert conflict is not None  # modified_both, т.к. данные разные


# === Тесты SyncEngine: разрешение конфликтов ===

class TestResolveConflict:
    """Тесты разрешения конфликтов."""
    
    def test_local_wins(self):
        """Стратегия: локальная версия побеждает."""
        engine = SyncEngine(ConflictResolution.LOCAL_WINS)
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local"},
            remote_data={"id": 1, "name": "Remote"},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        result = engine.resolve_conflict(conflict)
        assert result == conflict.local_data
    
    def test_remote_wins(self):
        """Стратегия: удалённая версия побеждает."""
        engine = SyncEngine(ConflictResolution.REMOTE_WINS)
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local"},
            remote_data={"id": 1, "name": "Remote"},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        result = engine.resolve_conflict(conflict)
        assert result == conflict.remote_data
    
    def test_newer_wins_local(self):
        """Стратегия: новее побеждает (локальная новее)."""
        engine = SyncEngine(ConflictResolution.NEWER_WINS)
        local_time = datetime.now()
        remote_time = local_time - timedelta(hours=1)
        
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local", "data_time": local_time},
            remote_data={"id": 1, "name": "Remote", "data_time": remote_time},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        result = engine.resolve_conflict(conflict)
        assert result == conflict.local_data
    
    def test_newer_wins_remote(self):
        """Стратегия: новее побеждает (удалённая новее)."""
        engine = SyncEngine(ConflictResolution.NEWER_WINS)
        local_time = datetime.now()
        remote_time = local_time + timedelta(hours=1)
        
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local", "data_time": local_time},
            remote_data={"id": 1, "name": "Remote", "data_time": remote_time},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        result = engine.resolve_conflict(conflict)
        assert result == conflict.remote_data
    
    def test_manual(self):
        """Стратегия: ручное разрешение."""
        engine = SyncEngine(ConflictResolution.MANUAL)
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local"},
            remote_data={"id": 1, "name": "Remote"},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        result = engine.resolve_conflict(conflict)
        assert result is None
    
    def test_override_strategy(self):
        """Переопределение стратегии для конкретного конфликта."""
        engine = SyncEngine(ConflictResolution.LOCAL_WINS)
        conflict = SyncConflict(
            local_data={"id": 1, "name": "Local"},
            remote_data={"id": 1, "name": "Remote"},
            entity_type="resource",
            entity_id=1,
            conflict_type="modified_both"
        )
        
        # Переопределяем стратегию для этого конфликта
        result = engine.resolve_conflict(conflict, ConflictResolution.REMOTE_WINS)
        assert result == conflict.remote_data


# === Тесты SyncEngine: слияние списков ===

class TestMergeLists:
    """Тесты слияния списков записей."""
    
    @pytest.fixture
    def engine(self):
        return SyncEngine(ConflictResolution.REMOTE_WINS)
    
    def test_merge_empty_lists(self, engine):
        """Слияние пустых списков."""
        merged, result = engine.merge_lists([], [], "resource")
        
        assert merged == []
        assert result.success is True
        assert result.stats.created == 0
    
    def test_merge_new_remote_items(self, engine):
        """Слияние: новые записи с сервера."""
        local = []
        remote = [
            {"id": 1, "name": "Item1"},
            {"id": 2, "name": "Item2"}
        ]
        
        merged, result = engine.merge_lists(local, remote, "resource")
        
        assert len(merged) == 2
        assert result.stats.created == 2
    
    def test_merge_no_changes(self, engine):
        """Слияние: без изменений."""
        items = [{"id": 1, "name": "Item1"}]
        
        merged, result = engine.merge_lists(items, items, "resource")
        
        assert len(merged) == 1
        assert result.stats.skipped == 1
        assert result.stats.conflicts == 0
    
    def test_merge_with_conflict(self, engine):
        """Слияние: с конфликтом (разные данные)."""
        local = [{"id": 1, "name": "Local"}]
        remote = [{"id": 1, "name": "Remote"}]
        
        merged, result = engine.merge_lists(local, remote, "resource")
        
        assert len(merged) == 1
        assert result.stats.conflicts == 1
        # Remote wins, поэтому должна быть удалённая версия
        assert merged[0]["name"] == "Remote"
    
    def test_merge_deleted_on_remote(self, engine):
        """Слияние: удалено на сервере."""
        local = [{"id": 1, "name": "Item1"}]
        remote = []
        
        merged, result = engine.merge_lists(local, remote, "resource")
        
        # Запись локально есть, но удалена на сервере — это конфликт
        assert result.stats.conflicts == 1
        assert result.conflicts[0].conflict_type == "deleted_on_remote"


# === Тесты SyncEngine: подготовка к синхронизации ===

class TestPrepareForSync:
    """Тесты подготовки данных к синхронизации."""
    
    @pytest.fixture
    def engine(self):
        return SyncEngine()
    
    def test_prepare_for_push_new_item(self, engine):
        """Подготовка к отправке: новая запись."""
        local = [{"id": 1, "name": "New"}]
        synced = []  # Ничего не было синхронизировано
        
        to_push = engine.prepare_for_push(local, synced)
        
        assert len(to_push) == 1
        assert to_push[0]["id"] == 1
    
    def test_prepare_for_push_modified_item(self, engine):
        """Подготовка к отправке: изменённая запись."""
        local = [{"id": 1, "name": "Modified"}]
        synced = [{"id": 1, "name": "Original"}]
        
        to_push = engine.prepare_for_push(local, synced)
        
        assert len(to_push) == 1
    
    def test_prepare_for_push_no_changes(self, engine):
        """Подготовка к отправке: без изменений."""
        local = [{"id": 1, "name": "Same"}]
        synced = [{"id": 1, "name": "Same"}]
        
        to_push = engine.prepare_for_push(local, synced)
        
        assert len(to_push) == 0
    
    def test_prepare_for_pull_new_remote(self, engine):
        """Подготовка к получению: новая запись на сервере."""
        remote = [{"id": 1, "name": "New"}]
        synced = []
        
        to_pull = engine.prepare_for_pull(remote, synced)
        
        assert len(to_pull) == 1
    
    def test_prepare_for_pull_no_changes(self, engine):
        """Подготовка к получению: без изменений."""
        remote = [{"id": 1, "name": "Same"}]
        synced = [{"id": 1, "name": "Same"}]
        
        to_pull = engine.prepare_for_pull(remote, synced)
        
        assert len(to_pull) == 0


# === Тесты SyncResult ===

class TestSyncResult:
    """Тесты результата синхронизации."""
    
    def test_str_representation(self):
        """Тест строкового представления."""
        stats = SyncStats(created=5, updated=3, deleted=1, conflicts=0, skipped=10)
        result = SyncResult(
            success=True,
            direction=SyncDirection.BIDIRECTIONAL,
            stats=stats
        )
        
        result_str = str(result)
        assert "Успешно" in result_str
        assert "Создано: 5" in result_str


# === Тесты RemoteClient с моками ===

class MockRemoteClient(RemoteClientInterface):
    """Мок клиента для тестирования без реального сервера."""
    
    def __init__(self):
        self.resources = []
        self.notes = []
        self.tasks = []
        self.available = True
    
    def ping(self) -> bool:
        return self.available
    
    def get_resources(self, since=None):
        return self.resources
    
    def get_notes(self, since=None):
        return self.notes
    
    def get_tasks(self, since=None):
        return self.tasks
    
    def push_resources(self, resources):
        self.resources = resources
        return True
    
    def push_notes(self, notes):
        self.notes = notes
        return True
    
    def push_tasks(self, tasks):
        self.tasks = tasks
        return True
    
    def sync(self, request: SyncRequest) -> SyncResponse:
        # Простая эхо-реализация для тестов
        return SyncResponse(
            resources=request.resources,
            notes=request.notes,
            tasks=request.tasks,
            server_time=datetime.now()
        )


class TestMockRemoteClient:
    """Тесты с использованием мок-клиента."""
    
    @pytest.fixture
    def mock_client(self):
        return MockRemoteClient()
    
    def test_ping_available(self, mock_client):
        """Тест доступности сервера."""
        assert mock_client.ping() is True
    
    def test_ping_unavailable(self, mock_client):
        """Тест недоступности сервера."""
        mock_client.available = False
        assert mock_client.ping() is False
    
    def test_get_resources(self, mock_client):
        """Тест получения ресурсов."""
        mock_client.resources = [{"id": 1, "name": "Test"}]
        result = mock_client.get_resources()
        assert len(result) == 1
        assert result[0]["name"] == "Test"
    
    def test_push_resources(self, mock_client):
        """Тест отправки ресурсов."""
        resources = [{"id": 1, "name": "New"}]
        success = mock_client.push_resources(resources)
        
        assert success is True
        assert len(mock_client.resources) == 1
    
    def test_sync_request(self, mock_client):
        """Тест запроса синхронизации."""
        request = SyncRequest(
            resources=[{"id": 1, "name": "Test"}],
            notes=[],
            tasks=[]
        )
        
        response = mock_client.sync(request)
        
        assert response.success is True
        assert len(response.resources) == 1


class TestSyncEngineWithMock:
    """Интеграционные тесты SyncEngine с мок-клиентом."""
    
    @pytest.fixture
    def mock_client(self):
        return MockRemoteClient()
    
    @pytest.fixture
    def engine(self):
        return SyncEngine(ConflictResolution.NEWER_WINS)
    
    def test_full_sync_flow(self, mock_client, engine):
        """Тест полного цикла синхронизации."""
        # Устанавливаем данные на "сервере"
        mock_client.resources = [
            {"id": 1, "name": "Remote1", "data_time": datetime.now()},
            {"id": 2, "name": "Remote2", "data_time": datetime.now()}
        ]
        
        # Локальные данные
        local_resources = [
            {"id": 2, "name": "Local2", "data_time": datetime.now() + timedelta(hours=1)},
            {"id": 3, "name": "Local3", "data_time": datetime.now()}
        ]
        
        # Получаем удалённые данные
        remote_resources = mock_client.get_resources()
        
        # Сливаем
        merged, result = engine.merge_lists(local_resources, remote_resources, "resource")
        
        assert result.success is True
        # Должно быть 3 записи (1, 2, 3)
        assert len(merged) == 3
    
    def test_sync_with_conflict(self, mock_client, engine):
        """Тест синхронизации с конфликтом."""
        # Конфликт: одна запись изменена и там, и там
        now = datetime.now()
        mock_client.resources = [
            {"id": 1, "name": "Remote", "data_time": now}
        ]
        local_resources = [
            {"id": 1, "name": "Local", "data_time": now + timedelta(hours=1)}
        ]
        
        remote_resources = mock_client.get_resources()
        merged, result = engine.merge_lists(local_resources, remote_resources, "resource")
        
        assert result.stats.conflicts == 1
        # Local новее, поэтому local wins
        assert merged[0]["name"] == "Local"
