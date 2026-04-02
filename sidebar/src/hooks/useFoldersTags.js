import { useState, useEffect, useCallback } from 'react';
import { foldersApi, tagsApi } from '../api/client';

/**
 * Хук для работы с папками и тегами.
 */
export function useFoldersTags() {
  const [folders, setFolders] = useState([]);
  const [tags, setTags] = useState([]);
  const [noteTags, setNoteTags] = useState({}); // noteId -> tags[]
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка папок
  const loadFolders = useCallback(async (categoryId = null, tree = true) => {
    try {
      const data = await foldersApi.getAll(categoryId, tree);
      setFolders(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load folders:', err);
      setFolders([]);
    }
  }, []);

  // Загрузка тегов
  const loadTags = useCallback(async () => {
    try {
      const data = await tagsApi.getAll();
      setTags(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load tags:', err);
      setTags([]);
    }
  }, []);

  // Загрузка тегов для заметки
  const loadNoteTags = useCallback(async (noteId) => {
    try {
      const data = await tagsApi.getForNote(noteId);
      setNoteTags(prev => ({ ...prev, [noteId]: data }));
      return data;
    } catch (err) {
      console.error('Failed to load note tags:', err);
      return [];
    }
  }, []);

  // Загрузка тегов для всех заметок
  const loadAllNoteTags = useCallback(async (noteIds) => {
    const tagsMap = {};
    for (const noteId of noteIds) {
      tagsMap[noteId] = await loadNoteTags(noteId);
    }
    setNoteTags(tagsMap);
  }, [loadNoteTags]);

  // Создание папки
  const createFolder = useCallback(async (name, parentId, noteCategoryId) => {
    return await foldersApi.create(name, parentId, noteCategoryId);
  }, []);

  // Удаление папки
  const deleteFolder = useCallback(async (id) => {
    await foldersApi.delete(id);
    setFolders(prev => prev.filter(f => f.id !== id));
  }, []);

  // Создание тега
  const createTag = useCallback(async (name, color) => {
    const created = await tagsApi.create(name, color);
    setTags(prev => [...prev, created]);
    return created;
  }, []);

  // Удаление тега
  const deleteTag = useCallback(async (id) => {
    await tagsApi.delete(id);
    setTags(prev => prev.filter(t => t.id !== id));
  }, []);

  // Добавление тега к заметке
  const addTagToNote = useCallback(async (noteId, tagId) => {
    await tagsApi.addTagToNote(noteId, tagId);
    // Обновляем локальное состояние
    const tag = tags.find(t => t.id === tagId);
    if (tag) {
      setNoteTags(prev => ({
        ...prev,
        [noteId]: [...(prev[noteId] || []), tag]
      }));
    }
  }, [tags]);

  // Удаление тега из заметки
  const removeTagFromNote = useCallback(async (noteId, tagId) => {
    await tagsApi.removeTagFromNote(noteId, tagId);
    setNoteTags(prev => ({
      ...prev,
      [noteId]: (prev[noteId] || []).filter(t => t.id !== tagId)
    }));
  }, []);

  // Получение тегов для заметки
  const getNoteTags = useCallback((noteId) => {
    return noteTags[noteId] || [];
  }, [noteTags]);

  // Загрузка при монтировании
  useEffect(() => {
    loadFolders();
    loadTags();
  }, [loadFolders, loadTags]);

  return {
    folders,
    tags,
    noteTags,
    loading,
    error,
    loadFolders,
    loadTags,
    loadNoteTags,
    loadAllNoteTags,
    createFolder,
    deleteFolder,
    createTag,
    deleteTag,
    addTagToNote,
    removeTagFromNote,
    getNoteTags,
  };
}

export default useFoldersTags;
