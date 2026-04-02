"""
Клиент для взаимодействия с удалённым сервером синхронизации.

Модуль предоставляет:
- HTTP-клиент для обмена данными с сервером
- Интерфейс для моков (тестирования без реального сервера)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

import requests


@dataclass
class SyncRequest:
    """Запрос на синхронизацию."""
    resources: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    last_sync: Optional[datetime] = None


@dataclass
class SyncResponse:
    """Ответ сервера на синхронизацию."""
    resources: List[Dict[str, Any]]
    notes: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    server_time: datetime
    success: bool = True
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class RemoteClientInterface(ABC):
    """
    Интерфейс клиента удалённого сервера.
    
    Используется для создания моков в тестах.
    """
    
    @abstractmethod
    def ping(self) -> bool:
        """Проверить доступность сервера."""
        pass
    
    @abstractmethod
    def get_resources(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список ресурсов с сервера."""
        pass
    
    @abstractmethod
    def get_notes(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список заметок с сервера."""
        pass
    
    @abstractmethod
    def get_tasks(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список задач с сервера."""
        pass
    
    @abstractmethod
    def push_resources(self, resources: List[Dict[str, Any]]) -> bool:
        """Отправить ресурсы на сервер."""
        pass
    
    @abstractmethod
    def push_notes(self, notes: List[Dict[str, Any]]) -> bool:
        """Отправить заметки на сервер."""
        pass
    
    @abstractmethod
    def push_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Отправить задачи на сервер."""
        pass
    
    @abstractmethod
    def sync(self, request: SyncRequest) -> SyncResponse:
        """Выполнить полную синхронизацию."""
        pass


class RemoteClient(RemoteClientInterface):
    """
    HTTP-клиент для взаимодействия с удалённым сервером синхронизации.
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Инициализировать клиент.
        
        Args:
            base_url: Базовый URL сервера (например, 'https://api.myinfomanager.com').
            api_key: API-ключ для аутентификации (если требуется).
            timeout: Таймаут запросов в секундах.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        
        if api_key:
            self._session.headers['Authorization'] = f'Bearer {api_key}'
    
    def ping(self) -> bool:
        """Проверить доступность сервера."""
        try:
            response = self._session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_resources(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список ресурсов с сервера."""
        params = {}
        if since:
            params['since'] = since.isoformat()
        
        response = self._session.get(
            f"{self.base_url}/api/sync/resources",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_notes(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список заметок с сервера."""
        params = {}
        if since:
            params['since'] = since.isoformat()
        
        response = self._session.get(
            f"{self.base_url}/api/sync/notes",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Получить список задач с сервера."""
        params = {}
        if since:
            params['since'] = since.isoformat()
        
        response = self._session.get(
            f"{self.base_url}/api/sync/tasks",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def push_resources(self, resources: List[Dict[str, Any]]) -> bool:
        """Отправить ресурсы на сервер."""
        response = self._session.post(
            f"{self.base_url}/api/sync/resources",
            json={"resources": resources},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 200
    
    def push_notes(self, notes: List[Dict[str, Any]]) -> bool:
        """Отправить заметки на сервер."""
        response = self._session.post(
            f"{self.base_url}/api/sync/notes",
            json={"notes": notes},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 200
    
    def push_tasks(self, tasks: List[Dict[str, Any]]) -> bool:
        """Отправить задачи на сервер."""
        response = self._session.post(
            f"{self.base_url}/api/sync/tasks",
            json={"tasks": tasks},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code == 200
    
    def sync(self, request: SyncRequest) -> SyncResponse:
        """
        Выполнить полную синхронизацию.
        
        Args:
            request: Запрос на синхронизацию.
        
        Returns:
            Ответ сервера.
        """
        payload = {
            "resources": request.resources,
            "notes": request.notes,
            "tasks": request.tasks,
        }
        
        if request.last_sync:
            payload["last_sync"] = request.last_sync.isoformat()
        
        response = self._session.post(
            f"{self.base_url}/api/sync",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        return SyncResponse(
            resources=data.get("resources", []),
            notes=data.get("notes", []),
            tasks=data.get("tasks", []),
            server_time=datetime.fromisoformat(data["server_time"]),
            success=data.get("success", True),
            errors=data.get("errors", [])
        )
    
    def close(self):
        """Закрыть сессию."""
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
