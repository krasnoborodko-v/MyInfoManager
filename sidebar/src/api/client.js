/**
 * API клиент для связи с бэкендом MyInfoManager.
 * При работе через собранный фронтенд (единый сервер) используется относительный путь.
 * При разработке (npm start) можно переменной окружения REACT_APP_API_URL указать отдельный бэкенд.
 */

// Определяем базовый URL API
// Electron: файл:// → нужен localhost
// Веб: относительный путь (статика на том же сервере)
const isElectron = window.electronAPI !== undefined;
const API_BASE_URL = isElectron
  ? (process.env.REACT_APP_API_URL || 'http://localhost:8000')
  : (process.env.REACT_APP_API_URL || '');

// ============================================================
// Авторизация
// ============================================================

const TOKEN_KEY = 'mim_access_token';
const REFRESH_KEY = 'mim_refresh_token';

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access, refresh) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return null;
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
    return data.access_token;
  } catch {
    return null;
  }
}

/**
 * Выполнить HTTP-запрос к API с автоматической подстановкой токена.
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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
    
    const token = getAuthToken();

    const response = await fetch(url, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
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
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/api/attachments/${id}/note`, {
      method: 'PUT',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
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
  
  getAttachmentData: (id) => {
    const token = getAuthToken();
    const tokenParam = token ? `&token=${encodeURIComponent(token)}` : '';
    return `${API_BASE_URL}/api/attachments/${id}?download=true${tokenParam}`;
  },
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

// === Контакты ===

export const contactsApi = {
  getAll: (groupId = null, favorite = false, search = null) => {
    const params = new URLSearchParams();
    if (groupId) params.append('group_id', groupId);
    if (favorite) params.append('favorite', 'true');
    if (search) params.append('search', search);
    return fetchApi(`/api/contacts?${params.toString()}`);
  },

  search: (query) => fetchApi(`/api/contacts/search?q=${encodeURIComponent(query)}`),

  getById: (id) => fetchApi(`/api/contacts/${id}`),

  create: (data) => fetchApi('/api/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  update: (id, data) => fetchApi(`/api/contacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  delete: (id) => fetchApi(`/api/contacts/${id}`, {
    method: 'DELETE',
  }),

  toggleFavorite: (id) => fetchApi(`/api/contacts/${id}/toggle-favorite`, {
    method: 'POST',
  }),

  // Группы
  getGroups: () => fetchApi('/api/contacts/groups'),

  createGroup: (name, color) => fetchApi(`/api/contacts/groups?name=${encodeURIComponent(name)}&color=${encodeURIComponent(color)}`, {
    method: 'POST',
  }),

  updateGroup: (id, data) => fetchApi(`/api/contacts/groups/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  deleteGroup: (id) => fetchApi(`/api/contacts/groups/${id}`, {
    method: 'DELETE',
  }),

  // Фото
  uploadPhoto: async (contactId, file) => {
    const formData = new FormData();
    formData.append('photo', file);
    const response = await fetch(`${API_BASE_URL}/api/contacts/${contactId}/photo`, {
      method: 'POST',  // Используем POST вместо PUT
      body: formData,
      // Не устанавливаем Content-Type - браузер сам установит multipart/form-data
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Ошибка загрузки фото');
    }
    return response.json();
  },

  deletePhoto: (contactId) => fetchApi(`/api/contacts/${contactId}/photo`, {
    method: 'DELETE',
  }),
};

// === Авторизация ===

export const authApi = {
  register: async (email, password, fullName = '') => {
    const res = await fetchApi('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    return res;
  },

  login: async (email, password) => {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || 'Login failed');
    }
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return data;
  },

  logout: () => {
    clearTokens();
  },

  me: async () => {
    return fetchApi('/auth/me');
  },
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
  contacts: contactsApi,
  checkServerHealth,
};
