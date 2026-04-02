import { useState, useEffect, useCallback } from 'react';
import { resourcesApi } from '../api/client';

/**
 * Хук для работы с ресурсами.
 * @returns {Object} - Состояние и методы для работы с ресурсами
 */
export function useResources() {
  const [resources, setResources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка ресурсов
  const loadResources = useCallback(async (kategoryId = null) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resourcesApi.getAll(kategoryId);
      setResources(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Загрузка категорий
  const loadCategories = useCallback(async () => {
    try {
      const data = await resourcesApi.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  }, []);

  // Поиск ресурсов
  const searchResources = useCallback(async (query) => {
    if (!query.trim()) {
      return loadResources();
    }
    try {
      setLoading(true);
      setError(null);
      const data = await resourcesApi.search(query);
      setResources(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [loadResources]);

  // Создание ресурса
  const createResource = useCallback(async (data) => {
    const created = await resourcesApi.create(data);
    setResources(prev => [...prev, created]);
    return created;
  }, []);

  // Обновление ресурса
  const updateResource = useCallback(async (id, data) => {
    const updated = await resourcesApi.update(id, data);
    setResources(prev => prev.map(r => r.id === id ? updated : r));
    return updated;
  }, []);

  // Удаление ресурса
  const deleteResource = useCallback(async (id) => {
    await resourcesApi.delete(id);
    setResources(prev => prev.filter(r => r.id !== id));
  }, []);

  // Создание категории
  const createCategory = useCallback(async (name) => {
    const created = await resourcesApi.createCategory(name);
    setCategories(prev => [...prev, created]);
    return created;
  }, []);

  // Удаление категории
  const deleteCategory = useCallback(async (id) => {
    await resourcesApi.deleteCategory(id);
    setCategories(prev => prev.filter(c => c.id !== id));
    setResources(prev => prev.filter(r => r.kategory_id !== id));
  }, []);

  // Загрузка при монтировании
  useEffect(() => {
    loadResources();
    loadCategories();
  }, [loadResources, loadCategories]);

  return {
    resources,
    categories,
    loading,
    error,
    loadResources,
    loadCategories,
    searchResources,
    createResource,
    updateResource,
    deleteResource,
    createCategory,
    deleteCategory,
  };
}

export default useResources;
