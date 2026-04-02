import { useState, useEffect, useCallback } from 'react';
import { notesApi } from '../api/client';

/**
 * Хук для работы с заметками.
 * @returns {Object} - Состояние и методы для работы с заметками
 */
export function useNotes() {
  const [notes, setNotes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attachmentsMap, setAttachmentsMap] = useState({}); // noteId -> attachments

  // Загрузка заметок
  const loadNotes = useCallback(async (kategoryId = null) => {
    try {
      setLoading(true);
      setError(null);
      const data = await notesApi.getAll(kategoryId);
      setNotes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Загрузка категорий
  const loadCategories = useCallback(async () => {
    try {
      const data = await notesApi.getCategories();
      setCategories(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load categories:', err);
      setCategories([]);
    }
  }, []);

  // Поиск заметок
  const searchNotes = useCallback(async (query) => {
    if (!query.trim()) {
      return loadNotes();
    }
    try {
      setLoading(true);
      setError(null);
      const data = await notesApi.search(query);
      setNotes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [loadNotes]);

  // Создание заметки
  const createNote = useCallback(async (data) => {
    const created = await notesApi.create(data);
    setNotes(prev => [...prev, created]);
    return created;
  }, []);

  // Обновление заметки
  const updateNote = useCallback(async (id, data) => {
    const updated = await notesApi.update(id, data);
    setNotes(prev => prev.map(n => n.id === id ? updated : n));
    return updated;
  }, []);

  // Перемещение заметки в папку
  const moveNoteToFolder = useCallback(async (noteId, folderId) => {
    const updated = await notesApi.moveNoteToFolder(noteId, folderId);
    setNotes(prev => prev.map(n => {
      if (n.id === noteId) {
        return { ...n, folder_id: folderId };
      }
      return n;
    }));
    return updated;
  }, []);

  // Удаление заметки
  const deleteNote = useCallback(async (id) => {
    await notesApi.delete(id);
    setNotes(prev => prev.filter(n => n.id !== id));
    setAttachmentsMap(prev => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }, []);

  // Создание категории
  const createCategory = useCallback(async (name) => {
    const created = await notesApi.createCategory(name);
    setCategories(prev => [...prev, created]);
    return created;
  }, []);

  // Удаление категории
  const deleteCategory = useCallback(async (id) => {
    await notesApi.deleteCategory(id);
    setCategories(prev => prev.filter(c => c.id !== id));
    setNotes(prev => prev.filter(n => n.kategory_id !== id));
  }, []);

  // === Вложения ===

  // Загрузка вложений для заметки
  const loadAttachments = useCallback(async (noteId) => {
    try {
      const attachments = await notesApi.getAttachments(noteId);
      setAttachmentsMap(prev => ({ ...prev, [noteId]: attachments }));
      return attachments;
    } catch (err) {
      console.error('Failed to load attachments:', err);
      setAttachmentsMap(prev => ({ ...prev, [noteId]: [] }));
      return [];
    }
  }, []);

  // Загрузка вложений для всех заметок
  const loadAllAttachments = useCallback(async () => {
    const attachmentsMap = {};
    for (const note of notes) {
      try {
        attachmentsMap[note.id] = await notesApi.getAttachments(note.id);
      } catch (err) {
        console.error(`Failed to load attachments for note ${note.id}:`, err);
        attachmentsMap[note.id] = [];
      }
    }
    setAttachmentsMap(attachmentsMap);
  }, [notes]);

  // Загрузка вложений при изменении списка заметок
  useEffect(() => {
    if (notes.length > 0) {
      loadAllAttachments();
    }
  }, [notes, loadAllAttachments]);

  // Загрузка вложения
  const uploadAttachment = useCallback(async (noteId, file) => {
    const attachment = await notesApi.uploadAttachment(noteId, file);
    setAttachmentsMap(prev => ({
      ...prev,
      [noteId]: [...(prev[noteId] || []), attachment]
    }));
    return attachment;
  }, []);

  // Удаление вложения
  const deleteAttachment = useCallback(async (noteId, attachmentId) => {
    await notesApi.deleteAttachment(attachmentId);
    setAttachmentsMap(prev => ({
      ...prev,
      [noteId]: (prev[noteId] || []).filter(a => a.id !== attachmentId)
    }));
  }, []);

  // Обновление примечания к вложению
  const updateAttachment = useCallback(async (attachmentId, note) => {
    return await notesApi.updateAttachment(attachmentId, note);
  }, []);

  // Получение URL для вложения
  const getAttachmentUrl = useCallback((attachmentId) => {
    return notesApi.getAttachmentData(attachmentId);
  }, []);

  // Загрузка при монтировании
  useEffect(() => {
    loadNotes();
    loadCategories();
  }, [loadNotes, loadCategories]);

  return {
    notes,
    categories,
    attachmentsMap,
    loading,
    error,
    loadNotes,
    loadCategories,
    searchNotes,
    createNote,
    updateNote,
    moveNoteToFolder,
    deleteNote,
    createCategory,
    deleteCategory,
    loadAttachments,
    uploadAttachment,
    updateAttachment,
    deleteAttachment,
    getAttachmentUrl,
  };
}

export default useNotes;
