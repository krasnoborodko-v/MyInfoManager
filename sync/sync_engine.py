"""
Ядро синхронизации данных между локальной и удалённой базой.

Модуль содержит логику:
- Сравнения версий записей по timestamp
- Обнаружения конфликтов (когда запись изменена и локально, и удалённо)
- Слияния данных с разрешением конфликтов
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from db.models import Resource, Note, Task


class ConflictResolution(Enum):
    """Стратегия разрешения конфликтов синхронизации."""
    LOCAL_WINS = "local_wins"      # Локальная версия всегда побеждает
    REMOTE_WINS = "remote_wins"    # Удалённая версия всегда побеждает
    NEWER_WINS = "newer_wins"      # Побеждает более новая версия (по timestamp)
    MANUAL = "manual"              # Требует ручного разрешения


class SyncDirection(Enum):
    """Направление синхронизации."""
    PUSH = "push"          # Локальное -> Удалённое
    PULL = "pull"          # Удалённое -> Локальное
    BIDIRECTIONAL = "both" # Двусторонняя синхронизация


@dataclass
class SyncConflict:
    """Представляет конфликт синхронизации."""
    local_data: Optional[Dict[str, Any]]
    remote_data: Optional[Dict[str, Any]]
    entity_type: str  # 'resource', 'note', 'task'
    entity_id: int
    conflict_type: str  # 'deleted_on_remote', 'modified_both', 'created_both'
    
    def __str__(self) -> str:
        return f"Конфликт {self.entity_type}#{self.entity_id}: {self.conflict_type}"


@dataclass
class SyncStats:
    """Статистика синхронизации."""
    created: int = 0
    updated: int = 0
    deleted: int = 0
    conflicts: int = 0
    skipped: int = 0
    
    def __str__(self) -> str:
        return (f"Создано: {self.created}, Обновлено: {self.updated}, "
                f"Удалено: {self.deleted}, Конфликтов: {self.conflicts}, "
                f"Пропущено: {self.skipped}")


@dataclass
class SyncResult:
    """Результат синхронизации."""
    success: bool
    direction: SyncDirection
    stats: SyncStats = field(default_factory=SyncStats)
    conflicts: List[SyncConflict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        status = "Успешно" if self.success else "Ошибка"
        return f"Синхронизация ({status}): {self.stats}"


T = TypeVar('T', bound=Dict[str, Any])


class SyncEngine:
    """
    Движок синхронизации данных.
    
    Отвечает за сравнение версий записей и слияние данных.
    Не зависит от способа передачи данных (HTTP, файл, etc).
    """
    
    def __init__(self, conflict_resolution: ConflictResolution = ConflictResolution.NEWER_WINS):
        """
        Инициализировать движок синхронизации.
        
        Args:
            conflict_resolution: Стратегия разрешения конфликтов по умолчанию.
        """
        self.conflict_resolution = conflict_resolution
    
    def compare_versions(
        self,
        local_updated: Optional[datetime],
        remote_updated: Optional[datetime]
    ) -> int:
        """
        Сравнить две версии по timestamp.
        
        Args:
            local_updated: Время последнего изменения локальной версии.
            remote_updated: Время последнего изменения удалённой версии.
        
        Returns:
            -1 если локальная версия старше,
             0 если версии равны,
             1 если локальная версия новее.
        """
        if local_updated is None and remote_updated is None:
            return 0
        if local_updated is None:
            return -1
        if remote_updated is None:
            return 1
        
        if local_updated < remote_updated:
            return -1
        elif local_updated > remote_updated:
            return 1
        else:
            return 0
    
    def detect_conflict(
        self,
        local_data: Optional[Dict[str, Any]],
        remote_data: Optional[Dict[str, Any]],
        entity_type: str
    ) -> Optional[SyncConflict]:
        """
        Обнаружить конфликт между локальной и удалённой версией.
        
        Args:
            local_data: Локальная версия записи (или None если удалена).
            remote_data: Удалённая версия записи (или None если удалена).
            entity_type: Тип сущности ('resource', 'note', 'task').
        
        Returns:
            SyncConflict если обнаружен конфликт, None иначе.
        """
        entity_id = None
        
        # Случай 1: Запись существует локально, но удалена удалённо
        if local_data is not None and remote_data is None:
            entity_id = local_data.get("id")
            return SyncConflict(
                local_data=local_data,
                remote_data=None,
                entity_type=entity_type,
                entity_id=entity_id,
                conflict_type="deleted_on_remote"
            )
        
        # Случай 2: Запись существует удалённо, но удалена локально
        if local_data is None and remote_data is not None:
            entity_id = remote_data.get("id")
            return SyncConflict(
                local_data=None,
                remote_data=remote_data,
                entity_type=entity_type,
                entity_id=entity_id,
                conflict_type="deleted_locally"
            )
        
        # Случай 3: Запись существует в обоих местах — проверяем на различия
        if local_data is not None and remote_data is not None:
            entity_id = local_data.get("id") or remote_data.get("id")
            
            # Сравниваем содержимое (исключая id и служебные поля)
            local_clean = self._clean_for_comparison(local_data)
            remote_clean = self._clean_for_comparison(remote_data)
            
            if local_clean != remote_clean:
                return SyncConflict(
                    local_data=local_data,
                    remote_data=remote_data,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    conflict_type="modified_both"
                )
        
        return None
    
    def _clean_for_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Очистить данные для сравнения (удалить служебные поля).
        
        Args:
            data: Исходные данные.
        
        Returns:
            Очищенные данные.
        """
        exclude_keys = {'id', 'created_at', 'updated_at', 'synced_at'}
        return {k: v for k, v in data.items() if k not in exclude_keys}
    
    def resolve_conflict(
        self,
        conflict: SyncConflict,
        strategy: Optional[ConflictResolution] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Разрешить конфликт синхронизации.
        
        Args:
            conflict: Конфликт для разрешения.
            strategy: Стратегия разрешения (если None, используется стратегия по умолчанию).
        
        Returns:
            Победившую версию данных или None если запись должна быть удалена.
        """
        strategy = strategy or self.conflict_resolution
        
        if strategy == ConflictResolution.LOCAL_WINS:
            return conflict.local_data
        
        elif strategy == ConflictResolution.REMOTE_WINS:
            return conflict.remote_data
        
        elif strategy == ConflictResolution.NEWER_WINS:
            local_time = self._get_timestamp(conflict.local_data)
            remote_time = self._get_timestamp(conflict.remote_data)
            
            cmp = self.compare_versions(local_time, remote_time)
            if cmp >= 0:
                return conflict.local_data
            else:
                return conflict.remote_data
        
        elif strategy == ConflictResolution.MANUAL:
            # При ручной стратегии возвращаем None — конфликт должен быть разрешён пользователем
            return None
        
        return conflict.remote_data  # По умолчанию remote wins
    
    def _get_timestamp(self, data: Optional[Dict[str, Any]]) -> Optional[datetime]:
        """
        Извлечь timestamp из данных.
        
        Args:
            data: Данные сущности.
        
        Returns:
            datetime или None.
        """
        if data is None:
            return None
        
        # Пробуем разные варианты имён поля timestamp
        for field_name in ['data_time', 'updated_at', 'timestamp', 'modified_at']:
            if field_name in data:
                value = data[field_name]
                if isinstance(value, datetime):
                    return value
                elif isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value)
                    except ValueError:
                        pass
        
        return None
    
    def merge_lists(
        self,
        local_items: List[Dict[str, Any]],
        remote_items: List[Dict[str, Any]],
        entity_type: str,
        strategy: Optional[ConflictResolution] = None
    ) -> tuple[List[Dict[str, Any]], SyncResult]:
        """
        Объединить два списка записей (локальный и удалённый).
        
        Args:
            local_items: Локальные записи.
            remote_items: Удалённые записи.
            entity_type: Тип сущности.
            strategy: Стратегия разрешения конфликтов.
        
        Returns:
            Кортеж (объединённый список, результат синхронизации).
        """
        result = SyncResult(
            success=True,
            direction=SyncDirection.BIDIRECTIONAL
        )
        
        # Индексируем по ID для быстрого поиска
        local_by_id = {item.get("id"): item for item in local_items if item.get("id")}
        remote_by_id = {item.get("id"): item for item in remote_items if item.get("id")}
        
        all_ids = set(local_by_id.keys()) | set(remote_by_id.keys())
        merged = []
        
        for item_id in all_ids:
            local_item = local_by_id.get(item_id)
            remote_item = remote_by_id.get(item_id)
            
            # Проверяем на конфликт
            conflict = self.detect_conflict(local_item, remote_item, entity_type)
            
            if conflict:
                result.stats.conflicts += 1
                resolved = self.resolve_conflict(conflict, strategy)
                
                if resolved is not None:
                    merged.append(resolved)
                    if local_item is None:
                        result.stats.created += 1
                    else:
                        result.stats.updated += 1
                else:
                    # Конфликт не разрешён (manual) — добавляем в список конфликтов
                    result.conflicts.append(conflict)
                    result.stats.skipped += 1
            else:
                # Конфликта нет — берём существующую запись
                item = remote_item or local_item
                if item:
                    merged.append(item)
                    
                    if local_item is None and remote_item is not None:
                        result.stats.created += 1
                    elif local_item is not None and remote_item is None:
                        result.stats.deleted += 1
                    else:
                        result.stats.skipped += 1
        
        return merged, result
    
    def prepare_for_push(
        self,
        local_items: List[Dict[str, Any]],
        synced_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Подготовить локальные изменения для отправки на сервер.
        
        Args:
            local_items: Текущие локальные записи.
            synced_items: Записи, которые были в последний раз синхронизированы.
        
        Returns:
            Список записей для отправки на сервер (изменённые и новые).
        """
        synced_by_id = {item.get("id"): item for item in synced_items if item.get("id")}
        to_push = []
        
        for local_item in local_items:
            item_id = local_item.get("id")
            synced_item = synced_by_id.get(item_id)
            
            if synced_item is None:
                # Новая запись — отправляем на сервер
                to_push.append(local_item)
            else:
                # Проверяем, изменилась ли запись
                local_clean = self._clean_for_comparison(local_item)
                synced_clean = self._clean_for_comparison(synced_item)
                
                if local_clean != synced_clean:
                    to_push.append(local_item)
        
        return to_push
    
    def prepare_for_pull(
        self,
        remote_items: List[Dict[str, Any]],
        synced_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Определить, какие записи нужно получить с сервера.
        
        Args:
            remote_items: Записи на сервере.
            synced_items: Записи, которые были в последний раз синхронизированы.
        
        Returns:
            Список записей для получения с сервера.
        """
        synced_by_id = {item.get("id"): item for item in synced_items if item.get("id")}
        to_pull = []
        
        for remote_item in remote_items:
            item_id = remote_item.get("id")
            synced_item = synced_by_id.get(item_id)
            
            if synced_item is None:
                # Новая запись на сервере — нужно получить
                to_pull.append(remote_item)
            else:
                # Проверяем, изменилась ли запись на сервере
                remote_clean = self._clean_for_comparison(remote_item)
                synced_clean = self._clean_for_comparison(synced_item)
                
                if remote_clean != synced_clean:
                    to_pull.append(remote_item)
        
        return to_pull
