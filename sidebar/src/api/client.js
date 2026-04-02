/**
 * API клиент для связи с бэкендом MyInfoManager.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Выполнить HTTP-запрос к API.
 * @param {string} endpoint - Эндпоинт API (например, '/api/resources')
 * @param {Object} options - Опции fetch
 * @returns {Promise<any>} - Ответ сервера
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка ${response.status}: ${response.statusText}`);
    }

    // Пустой ответ (например, при DELETE)
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    // Проверка на ошибку сети (сервер недоступен)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error(`Network error (${endpoint}): Сервер недоступен. Проверьте, запущен ли бэкенд на ${API_BASE_URL}`);
      throw new Error(`Сервер недоступен. Проверьте, запущен ли бэкенд на ${API_BASE_URL}`);
    }
    console.error(`API error (${endpoint}):`, error);
    throw error;
  }
}

// === Ресурсы ===

export const resourcesApi = {
  getAll: (kategoryId = null) => {
    const params = kategoryId ? `?kategory_id=${kategoryId}` : '';
    return fetchApi(`/api/resources${params}`);
  },
  
  getById: (id) => fetchApi(`/api/resources/${id}`),
  
  search: (query) => fetchApi(`/api/resources/search?q=${encodeURIComponent(query)}`),
  
  create: (data) => fetchApi('/api/resources', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  update: (id, data) => fetchApi(`/api/resources/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  delete: (id) => fetchApi(`/api/resources/${id}`, {
    method: 'DELETE',
  }),
  
  // Категории ресурсов
  getCategories: () => fetchApi('/api/resources/categories'),
  
  createCategory: (name) => fetchApi(`/api/resources/categories?name=${encodeURIComponent(name)}`, {
    method: 'POST',
  }),
  
  deleteCategory: (id) => fetchApi(`/api/resources/categories/${id}`, {
    method: 'DELETE',
  }),
};

// === Заметки ===

export const notesApi = {
  getAll: (kategoryId = null) => {
    const params = kategoryId ? `?kategory_id=${kategoryId}` : '';
    return fetchApi(`/api/notes${params}`);
  },
  
  getById: (id) => fetchApi(`/api/notes/${id}`),
  
  search: (query) => fetchApi(`/api/notes/search?q=${encodeURIComponent(query)}`),
  
  create: (data) => fetchApi('/api/notes', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  update: (id, data) => fetchApi(`/api/notes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  moveNoteToFolder: async (noteId, folderId) => {
    const response = await fetchApi(`/api/notes/${noteId}/folder`, {
      method: 'PATCH',
      body: JSON.stringify({ folder_id: folderId }),
    });
    return response;
  },

  delete: (id) => fetchApi(`/api/notes/${id}`, {
    method: 'DELETE',
  }),
  
  // Категории заметок
  getCategories: () => fetchApi('/api/notes/categories'),
  
  createCategory: (name) => fetchApi(`/api/notes/categories?name=${encodeURIComponent(name)}`, {
    method: 'POST',
  }),
  
  deleteCategory: (id) => fetchApi(`/api/notes/categories/${id}`, {
    method: 'DELETE',
  }),
  
  // Вложения
  getAttachments: (noteId) => fetchApi(`/api/attachments/note/${noteId}`),
  
  uploadAttachment: async (noteId, file, note = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (note) {
      formData.append('note', note);
    }
    
    const url = `${API_BASE_URL}/api/attachments/note/${noteId}`;
    
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  updateAttachment: async (id, note) => {
    const formData = new FormData();
    formData.append('note', note);
    
    const response = await fetch(`${API_BASE_URL}/api/attachments/${id}/note`, {
      method: 'PUT',
      body: formData,
      // Не устанавливаем Content-Type - браузер сам установит multipart/form-data с boundary
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },
  
  deleteAttachment: (id) => fetchApi(`/api/attachments/${id}`, {
    method: 'DELETE',
  }),
  
  getAttachmentData: (id) => `${API_BASE_URL}/api/attachments/${id}?download=true`,
};

// === Настройки ===

export const settingsApi = {
  getAll: () => fetchApi('/api/settings'),

  get: (key) => fetchApi(`/api/settings/${key}`),

  update: async (key, value) => {
    const formData = new FormData();
    formData.append('value', value);
    
    const response = await fetch(`${API_BASE_URL}/api/settings/${key}`, {
      method: 'PUT',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },
};

// === Папки и теги ===

export const foldersApi = {
  getAll: (categoryId = null, tree = false) => {
    const params = new URLSearchParams();
    if (categoryId) params.append('category_id', categoryId);
    if (tree) params.append('tree', 'true');
    return fetchApi(`/api/folders?${params}`);
  },

  create: (name, parentId, noteCategoryId) => fetchApi('/api/folders', {
    method: 'POST',
    body: JSON.stringify({ name, parent_id: parentId, note_category_id: noteCategoryId }),
  }),

  update: (id, name, parentId, noteCategoryId) => fetchApi(`/api/folders/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ name, parent_id: parentId, note_category_id: noteCategoryId }),
  }),

  delete: (id) => fetchApi(`/api/folders/${id}`, {
    method: 'DELETE',
  }),
};

export const tagsApi = {
  getAll: () => fetchApi('/api/tags'),

  create: (name, color) => fetchApi('/api/tags', {
    method: 'POST',
    body: JSON.stringify({ name, color }),
  }),

  update: (id, name, color) => fetchApi(`/api/tags/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ name, color }),
  }),

  delete: (id) => fetchApi(`/api/tags/${id}`, {
    method: 'DELETE',
  }),

  // Теги заметки
  getForNote: (noteId) => fetchApi(`/api/notes/${noteId}/tags`),

  addTagToNote: (noteId, tagId) => fetchApi(`/api/notes/${noteId}/tags`, {
    method: 'POST',
    body: JSON.stringify({ tag_id: tagId }),
  }),

  removeTagFromNote: (noteId, tagId) => fetchApi(`/api/notes/${noteId}/tags/${tagId}`, {
    method: 'DELETE',
  }),

  setTagsForNote: (noteId, tagIds) => fetchApi(`/api/notes/${noteId}/tags`, {
    method: 'PUT',
    body: JSON.stringify({ tag_ids: tagIds }),
  }),
};

// === Задачи ===

export const tasksApi = {
  getAll: (kategoryId = null) => {
    const params = kategoryId ? `?kategory_id=${kategoryId}` : '';
    return fetchApi(`/api/tasks${params}`);
  },

  getById: (id) => fetchApi(`/api/tasks/${id}`),

  search: (query) => fetchApi(`/api/tasks/search?q=${encodeURIComponent(query)}`),

  create: (data) => fetchApi('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  update: (id, data) => fetchApi(`/api/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  delete: (id) => fetchApi(`/api/tasks/${id}`, {
    method: 'DELETE',
  }),

  // Категории задач
  getCategories: () => fetchApi('/api/tasks/categories'),

  createCategory: (name) => fetchApi(`/api/tasks/categories?name=${encodeURIComponent(name)}`, {
    method: 'POST',
  }),

  deleteCategory: (id) => fetchApi(`/api/tasks/categories/${id}`, {
    method: 'DELETE',
  }),

  // Подзадачи
  getSubtasks: (taskId) => fetchApi(`/api/tasks/${taskId}/subtasks`),

  createSubtask: (taskId, data) => fetchApi(`/api/tasks/${taskId}/subtasks`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  updateSubtask: (taskId, subtaskId, data) => fetchApi(`/api/tasks/${taskId}/subtasks/${subtaskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  deleteSubtask: (taskId, subtaskId) => fetchApi(`/api/tasks/${taskId}/subtasks/${subtaskId}`, {
    method: 'DELETE',
  }),
};

// === Проверка доступности сервера ===

export const checkServerHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

export default {
  resources: resourcesApi,
  notes: notesApi,
  tasks: tasksApi,
  checkServerHealth,
};
