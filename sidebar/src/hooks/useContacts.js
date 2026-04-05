import { useState, useEffect, useCallback } from 'react';
import { contactsApi } from '../api/client';

/**
 * Хук для работы с контактами.
 * @returns {Object} - Состояние и методы для работы с контактами
 */
export function useContacts() {
  const [contacts, setContacts] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка контактов
  const loadContacts = useCallback(async (groupId = null, favorite = false, search = null) => {
    try {
      setLoading(true);
      setError(null);
      const data = await contactsApi.getAll(groupId, favorite, search);
      setContacts(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Загрузка групп
  const loadGroups = useCallback(async () => {
    try {
      const data = await contactsApi.getGroups();
      setGroups(data);
    } catch (err) {
      console.error('Failed to load groups:', err);
    }
  }, []);

  // Поиск контактов
  const searchContacts = useCallback(async (query) => {
    if (!query.trim()) {
      return loadContacts();
    }
    try {
      setLoading(true);
      setError(null);
      const data = await contactsApi.search(query);
      setContacts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [loadContacts]);

  // Создание контакта
  const createContact = useCallback(async (data) => {
    // Приводим данные к формату, который ждет сервер (строки вместо JSON-строк)
    const cleanData = {};
    for (const [key, value] of Object.entries(data)) {
      if (['phones', 'emails', 'socials'].includes(key) && typeof value === 'string') {
        try {
          const parsed = JSON.parse(value);
          // Сервер ждет строку, но если это массив объектов, превратим в строку
          cleanData[key] = Array.isArray(parsed) 
            ? parsed.map(p => typeof p === 'object' ? (p.value || p.phone || p.email || '') : p).join(', ')
            : value;
        } catch {
          cleanData[key] = value;
        }
      } else {
        cleanData[key] = value;
      }
    }
    cleanData.user_id = userId;

    const created = await contactsApi.create(cleanData);
    setContacts(prev => [...prev, created]);
    return created;
  }, [userId]);

  // Обновление контакта
  const updateContact = useCallback(async (id, data) => {
    const cleanData = {};
    for (const [key, value] of Object.entries(data)) {
      if (['phones', 'emails', 'socials'].includes(key) && typeof value === 'string') {
        try {
          const parsed = JSON.parse(value);
          cleanData[key] = Array.isArray(parsed) 
            ? parsed.map(p => typeof p === 'object' ? (p.value || p.phone || p.email || '') : p).join(', ')
            : value;
        } catch {
          cleanData[key] = value;
        }
      } else {
        cleanData[key] = value;
      }
    }
    const updated = await contactsApi.update(id, cleanData);
    setContacts(prev => prev.map(c => c.id === id ? updated : c));
    return updated;
  }, []);

  // Удаление контакта
  const deleteContact = useCallback(async (id) => {
    await contactsApi.delete(id);
    setContacts(prev => prev.filter(c => c.id !== id));
  }, []);

  // Переключение избранного
  const toggleFavorite = useCallback(async (id) => {
    const updated = await contactsApi.toggleFavorite(id);
    setContacts(prev => prev.map(c => c.id === id ? updated : c));
    return updated;
  }, []);

  // Загрузка контакта по ID
  const getContactById = useCallback(async (id) => {
    return await contactsApi.getById(id);
  }, []);

  // Создание группы
  const createGroup = useCallback(async (name, color) => {
    const created = await contactsApi.createGroup(name, color);
    setGroups(prev => [...prev, created]);
    return created;
  }, []);

  // Обновление группы
  const updateGroup = useCallback(async (id, data) => {
    const updated = await contactsApi.updateGroup(id, data);
    setGroups(prev => prev.map(g => g.id === id ? updated : g));
    return updated;
  }, []);

  // Удаление группы
  const deleteGroup = useCallback(async (id) => {
    await contactsApi.deleteGroup(id);
    setGroups(prev => prev.filter(g => g.id !== id));
  }, []);

  // Загрузка фото контакта
  const uploadPhoto = useCallback(async (contactId, file) => {
    return await contactsApi.uploadPhoto(contactId, file);
  }, []);

  // Удаление фото контакта
  const deletePhoto = useCallback(async (contactId) => {
    return await contactsApi.deletePhoto(contactId);
  }, []);

  // Инициализация при монтировании
  useEffect(() => {
    loadContacts();
    loadGroups();
  }, [loadContacts, loadGroups]);

  return {
    contacts,
    groups,
    loading,
    error,
    loadContacts,
    loadGroups,
    searchContacts,
    createContact,
    updateContact,
    deleteContact,
    toggleFavorite,
    getContactById,
    createGroup,
    updateGroup,
    deleteGroup,
    uploadPhoto,
    deletePhoto,
  };
}
