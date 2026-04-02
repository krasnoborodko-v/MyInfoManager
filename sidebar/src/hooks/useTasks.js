import { useState, useEffect, useCallback } from 'react';
import { tasksApi } from '../api/client';

/**
 * Хук для работы с задачами.
 * @returns {Object} - Состояние и методы для работы с задачами
 */
export function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [subtasks, setSubtasks] = useState({}); // subtasks[taskId] = array of subtasks
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка задач
  const loadTasks = useCallback(async (kategoryId = null) => {
    try {
      setLoading(true);
      setError(null);
      const data = await tasksApi.getAll(kategoryId);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Загрузка категорий
  const loadCategories = useCallback(async () => {
    try {
      const data = await tasksApi.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  }, []);

  // Загрузка подзадач для задачи
  const loadSubtasks = useCallback(async (taskId) => {
    try {
      const data = await tasksApi.getSubtasks(taskId);
      setSubtasks(prev => ({ ...prev, [taskId]: data }));
      return data;
    } catch (err) {
      console.error('Failed to load subtasks:', err);
      return [];
    }
  }, []);

  // Поиск задач
  const searchTasks = useCallback(async (query) => {
    if (!query.trim()) {
      return loadTasks();
    }
    try {
      setLoading(true);
      setError(null);
      const data = await tasksApi.search(query);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [loadTasks]);

  // Создание задачи
  const createTask = useCallback(async (data) => {
    const created = await tasksApi.create(data);
    // Перезагружаем все задачи, чтобы получить актуальный список
    await loadTasks();
    return created;
  }, [loadTasks]);

  // Обновление задачи
  const updateTask = useCallback(async (id, data) => {
    const updated = await tasksApi.update(id, data);
    setTasks(prev => prev.map(t => t.id === id ? updated : t));
    return updated;
  }, []);

  // Удаление задачи
  const deleteTask = useCallback(async (id) => {
    await tasksApi.delete(id);
    setTasks(prev => prev.filter(t => t.id !== id));
    setSubtasks(prev => {
      const newState = { ...prev };
      delete newState[id];
      return newState;
    });
  }, []);

  // Создание подзадачи
  const createSubtask = useCallback(async (taskId, data) => {
    const created = await tasksApi.createSubtask(taskId, data);
    setSubtasks(prev => ({
      ...prev,
      [taskId]: [...(prev[taskId] || []), created]
    }));
    return created;
  }, []);

  // Обновление подзадачи
  const updateSubtask = useCallback(async (taskId, subtaskId, data) => {
    const updated = await tasksApi.updateSubtask(taskId, subtaskId, data);
    setSubtasks(prev => ({
      ...prev,
      [taskId]: prev[taskId].map(s => s.id === subtaskId ? updated : s)
    }));
    return updated;
  }, []);

  // Удаление подзадачи
  const deleteSubtask = useCallback(async (taskId, subtaskId) => {
    await tasksApi.deleteSubtask(taskId, subtaskId);
    setSubtasks(prev => ({
      ...prev,
      [taskId]: prev[taskId].filter(s => s.id !== subtaskId)
    }));
  }, []);

  // Создание категории
  const createCategory = useCallback(async (name) => {
    const created = await tasksApi.createCategory(name);
    setCategories(prev => [...prev, created]);
    return created;
  }, []);

  // Удаление категории
  const deleteCategory = useCallback(async (id) => {
    await tasksApi.deleteCategory(id);
    setCategories(prev => prev.filter(c => c.id !== id));
    setTasks(prev => prev.filter(t => t.kategory_id !== id));
  }, []);

  // Загрузка при монтировании
  useEffect(() => {
    loadTasks();
    loadCategories();
  }, [loadTasks, loadCategories]);

  return {
    tasks,
    categories,
    subtasks,
    loading,
    error,
    loadTasks,
    loadCategories,
    loadSubtasks,
    searchTasks,
    createTask,
    updateTask,
    deleteTask,
    createSubtask,
    updateSubtask,
    deleteSubtask,
    createCategory,
    deleteCategory,
  };
}

export default useTasks;
