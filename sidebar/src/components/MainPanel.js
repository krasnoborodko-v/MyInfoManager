import React, { useState } from 'react';
import {
  FolderTree,
  FileText,
  CheckSquare,
  Calendar,
  Clock,
  Settings,
  ExternalLink,
  Edit,
  Trash2,
  Save,
  X,
  Mic,
  ChevronRight,
  Plus
} from 'lucide-react';
import { useResources, useNotes, useTasks, useSettings, useFoldersTags } from '../hooks';
import AudioRecorder from './AudioRecorder';
import './MainPanel.css';

const sectionConfig = {
  resources: { icon: FolderTree, title: 'Ресурсы', description: 'Список информационных ресурсов' },
  notes: { icon: FileText, title: 'Заметки', description: 'Ваши заметки и идеи' },
  tasks: { icon: CheckSquare, title: 'Задачи', description: 'Список задач' },
  calendar: { icon: Calendar, title: 'Календарь', description: 'Календарь событий' },
  planner: { icon: Clock, title: 'Планировщик', description: 'План на день' },
  settings: { icon: Settings, title: 'Настройки', description: 'Настройки приложения' },
};

function MainPanel({ activeSection, selectedItemId, onItemSelect }) {
  const config = sectionConfig[activeSection];
  const Icon = config?.icon;
  
  const selectedId = typeof selectedItemId === 'object' ? selectedItemId?.id : selectedItemId;
  const selectedType = typeof selectedItemId === 'object' ? selectedItemId?.type : activeSection;

  return (
    <div className="main-panel">
      <div className="main-content">
        <div className="section-header">
          {Icon && <Icon size={32} />}
          <h1>{config?.title}</h1>
        </div>
        <p className="section-description">{config?.description}</p>

        {selectedId ? (
          <div className="item-detail">
            {selectedType === 'resource' && (
              <ResourceDetail id={selectedId} onClose={() => onItemSelect(null)} />
            )}
            {selectedType === 'note' && (
              <NoteDetail id={selectedId} onClose={() => onItemSelect(null)} />
            )}
            {selectedType === 'task' && (
              <TaskDetail id={selectedId} onClose={() => onItemSelect(null)} />
            )}
          </div>
        ) : (
          <div className="placeholder-content">
            <div className="placeholder-box">
              <p>Выберите элемент в sidebar для просмотра и редактирования</p>
              <p className="hint">Используйте поиск для быстрого нахождения нужного элемента</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// === Детали ресурса ===

function ResourceDetail({ id, onClose }) {
  const { resources, categories, updateResource, deleteResource } = useResources();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(null);

  const resource = resources.find(r => r.id === id);
  
  React.useEffect(() => {
    if (resource) {
      setEditData({ ...resource });
    }
  }, [resource]);

  if (!resource) {
    return <div className="not-found">Ресурс не найден</div>;
  }

  const handleSave = async () => {
    await updateResource(resource.id, editData);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Удалить этот ресурс?')) {
      await deleteResource(resource.id);
      onClose();
    }
  };

  const category = categories.find(c => c.id === resource.kategory_id);

  if (isEditing && editData) {
    return (
      <div className="edit-form">
        <div className="form-header">
          <h3>Редактирование ресурса</h3>
          <div className="form-actions">
            <button onClick={handleSave} className="save-btn">
              <Save size={16} /> Сохранить
            </button>
            <button onClick={() => setIsEditing(false)} className="cancel-btn">
              <X size={16} /> Отмена
            </button>
          </div>
        </div>
        <div className="form-body">
          <div className="form-group">
            <label>Название</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Категория</label>
            <select
              value={editData.kategory_id || ''}
              onChange={(e) => setEditData({ ...editData, kategory_id: parseInt(e.target.value) || null })}
            >
              <option value="">Без категории</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>URL</label>
            <input
              type="url"
              value={editData.url || ''}
              onChange={(e) => setEditData({ ...editData, url: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={editData.description || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-view">
      <div className="detail-header">
        <h2>{resource.name}</h2>
        <div className="detail-actions">
          <button onClick={() => setIsEditing(true)} className="edit-btn">
            <Edit size={16} /> Редактировать
          </button>
          <button onClick={handleDelete} className="delete-btn">
            <Trash2 size={16} /> Удалить
          </button>
          <button onClick={onClose} className="close-btn">
            <X size={16} /> Закрыть
          </button>
        </div>
      </div>
      <div className="detail-body">
        {category && (
          <div className="detail-row">
            <span className="label">Категория:</span>
            <span className="value">{category.name}</span>
          </div>
        )}
        {resource.url && (
          <div className="detail-row">
            <span className="label">URL:</span>
            <span className="value">
              <a href={resource.url} target="_blank" rel="noopener noreferrer">
                {resource.url} <ExternalLink size={12} />
              </a>
            </span>
          </div>
        )}
        {resource.description && (
          <div className="detail-row">
            <span className="label">Описание:</span>
            <p className="description">{resource.description}</p>
          </div>
        )}
      </div>
    </div>
  );
}

// === Детали заметки ===

function NoteDetail({ id, onClose }) {
  const { notes, categories, updateNote, deleteNote, attachmentsMap, uploadAttachment, deleteAttachment, getAttachmentUrl, updateAttachment, loadAttachments } = useNotes();
  const { getSetting } = useSettings();
  const { tags, addTagToNote, removeTagFromNote, getNoteTags, loadNoteTags, createTag } = useFoldersTags();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [expandedImage, setExpandedImage] = useState(null);
  const [editingNote, setEditingNote] = useState({ id: null, text: '' });
  const [showRecorder, setShowRecorder] = useState(false);
  const [showTags, setShowTags] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#008888');

  const note = notes.find(n => n.id === id);
  const attachments = attachmentsMap?.[id] || [];
  const noteTags = getNoteTags(id);
  
  // Получаем лимит аудио (по умолчанию 5)
  const audioLimit = parseInt(getSetting('audio_limit', '5')) || 5;
  
  // Разделяем вложения по типам
  const images = attachments.filter(att => att.file_type.startsWith('image/'));
  const audios = attachments.filter(att => att.file_type.startsWith('audio/'));
  // Ограничиваем количество аудио
  const displayedAudios = audios.slice(0, audioLimit);
  const hiddenAudiosCount = audios.length - audioLimit;

  React.useEffect(() => {
    if (note) {
      setEditData({ ...note });
      loadNoteTags(note.id);
    }
  }, [note, loadNoteTags]);

  if (!note) {
    return <div className="not-found">Заметка не найдена</div>;
  }

  const handleSave = async () => {
    await updateNote(note.id, editData);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Удалить эту заметку?')) {
      await deleteNote(note.id);
      onClose();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
                          'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/webm'];
    if (!allowedTypes.includes(file.type)) {
      alert('Неподдерживаемый тип файла. Разрешены изображения и аудио.');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      alert('Файл слишком большой (макс. 10MB)');
      return;
    }
    
    try {
      setUploading(true);
      await uploadAttachment(note.id, file, '');
    } catch (err) {
      alert('Ошибка загрузки: ' + err.message);
    } finally {
      setUploading(false);
    }
    e.target.value = '';
  };

  const handleRecordingComplete = async (audioFile) => {
    try {
      setUploading(true);
      await uploadAttachment(note.id, audioFile, 'Голосовое сообщение');
      setShowRecorder(false);
    } catch (err) {
      alert('Ошибка сохранения записи: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleCreateTag = async () => {
    if (newTagName.trim()) {
      try {
        const created = await createTag(newTagName.trim(), newTagColor);
        setNewTagName('');
        setShowTags(false);
        // Теги обновятся автоматически через useFoldersTags
      } catch (err) {
        alert('Ошибка создания тега: ' + err.message);
      }
    }
  };

  const handleToggleTag = async (tagId) => {
    const isAdded = noteTags.some(t => t.id === tagId);
    if (isAdded) {
      await removeTagFromNote(note.id, tagId);
    } else {
      await addTagToNote(note.id, tagId);
    }
    // Закрываем окно выбора тегов после добавления/удаления
    setShowTags(false);
  };

  const handleDeleteAttachment = async (attachmentId) => {
    if (window.confirm('Удалить вложение?')) {
      await deleteAttachment(note.id, attachmentId);
    }
  };

  const handleUpdateNote = async (attachmentId, text) => {
    try {
      await updateAttachment(attachmentId, text);
      // Обновляем attachmentsMap локально
      const updatedAttachments = attachments.map(att => 
        att.id === attachmentId ? { ...att, note: text } : att
      );
      setEditingNote({ id: null, text: '' });
      // Принудительно триггерим обновление через loadAttachments
      await loadAttachments(note.id);
    } catch (err) {
      alert('Ошибка сохранения: ' + err.message);
    }
  };

  const category = categories.find(c => c.id === note.kategory_id);

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (isEditing && editData) {
    return (
      <div className="edit-form">
        <div className="form-header">
          <h3>Редактирование заметки</h3>
          <div className="form-actions">
            <button onClick={handleSave} className="save-btn">
              <Save size={16} /> Сохранить
            </button>
            <button onClick={() => setIsEditing(false)} className="cancel-btn">
              <X size={16} /> Отмена
            </button>
          </div>
        </div>
        <div className="form-body">
          <div className="form-group">
            <label>Название</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Категория</label>
            <select
              value={editData.kategory_id || ''}
              onChange={(e) => setEditData({ ...editData, kategory_id: parseInt(e.target.value) || null })}
            >
              <option value="">Без категории</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Текст</label>
            <textarea
              value={editData.note_text || ''}
              onChange={(e) => setEditData({ ...editData, note_text: e.target.value })}
              rows={10}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-view">
      <div className="detail-header">
        <h2>{note.name}</h2>
        <div className="detail-actions">
          <button onClick={() => setIsEditing(true)} className="edit-btn">
            <Edit size={16} /> Редактировать
          </button>
          <button onClick={handleDelete} className="delete-btn">
            <Trash2 size={16} /> Удалить
          </button>
          <button onClick={onClose} className="close-btn">
            <X size={16} /> Закрыть
          </button>
        </div>
      </div>
      <div className="detail-body">
        <div className="detail-row meta-info">
          {category && (
            <div className="meta-item">
              <span className="label">Категория:</span>
              <span className="value">{category.name}</span>
            </div>
          )}
          <div className="meta-item">
            <span className="label">Дата:</span>
            <span className="value">{formatDate(note.data_time)}</span>
          </div>
        </div>

        {/* Теги */}
        <div className="detail-row tags-section">
          <div className="tags-header">
            <span className="label">Теги:</span>
            <button className="add-tag-btn" onClick={() => setShowTags(!showTags)}>
              + Тег
            </button>
          </div>
          <div className="tags-content">
            <div className="tags-list">
              {noteTags.map(tag => (
                <span 
                  key={tag.id} 
                  className="tag-item"
                  style={{ backgroundColor: tag.color + '33', borderColor: tag.color }}
                >
                  {tag.name}
                  <button onClick={() => handleToggleTag(tag.id)}>×</button>
                </span>
              ))}
            </div>
            
            {showTags && (
              <div className="tag-selector">
                <div className="tag-search">
                  <input
                    type="text"
                    placeholder="Создать новый тег..."
                    value={newTagName}
                    onChange={(e) => setNewTagName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleCreateTag()}
                  />
                  <input
                    type="color"
                    value={newTagColor}
                    onChange={(e) => setNewTagColor(e.target.value)}
                  />
                  <button onClick={handleCreateTag}>OK</button>
                </div>
                <div className="existing-tags">
                  {tags.map(tag => {
                    const isAdded = noteTags.some(t => t.id === tag.id);
                    return (
                      <button
                        key={tag.id}
                        className={`tag-option ${isAdded ? 'added' : ''}`}
                        onClick={() => handleToggleTag(tag.id)}
                        style={{ borderColor: tag.color }}
                      >
                        <span style={{ color: tag.color }}>{tag.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {note.note_text && (
          <div className="detail-row">
            <span className="label">Текст:</span>
            <p className="description">{note.note_text}</p>
          </div>
        )}
        
        {/* Вложения - Изображения */}
        <div className="detail-row attachments-section">
          <div className="attachments-header">
            <span className="label">Изображения:</span>
            <div className="attachments-actions">
              <label className="upload-btn" title="Изображения: JPEG, PNG, GIF, WebP">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  style={{ display: 'none' }}
                />
                📎 Добавить
              </label>
              {uploading && <span className="uploading">Загрузка...</span>}
            </div>
          </div>
          <div className="attachments-content">
            
            {images.length > 0 && (
              <div className="image-gallery">
                {images.map(att => {
                  const url = getAttachmentUrl(att.id);
                  const isEditing = editingNote.id === att.id;
                  
                  return (
                    <div key={att.id} className="image-item">
                      <div 
                        className="image-thumbnail" 
                        onClick={() => setExpandedImage(url)}
                        style={{ backgroundImage: `url(${url})` }}
                      />
                      <div className="image-note">
                        {isEditing ? (
                          <>
                            <textarea
                              value={editingNote.text}
                              onChange={(e) => setEditingNote({ id: att.id, text: e.target.value })}
                              placeholder="Примечание..."
                            />
                            <div className="note-actions">
                              <button onClick={() => handleUpdateNote(att.id, editingNote.text)}>OK</button>
                              <button onClick={() => setEditingNote({ id: null, text: '' })}>X</button>
                            </div>
                          </>
                        ) : (
                          <>
                            <span onClick={() => setEditingNote({ id: att.id, text: att.note || '' })}>
                              {att.note || 'Добавить примечание'}
                            </span>
                            <button
                              className="delete-btn"
                              onClick={() => handleDeleteAttachment(att.id)}
                            >
                              <Trash2 size={12} />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
        
        {/* Вложения - Аудио */}
        <div className="detail-row attachments-section">
          <div className="attachments-header">
            <span className="label">Аудио:</span>
            <div className="attachments-actions">
              <label className="upload-btn" title="Аудио: MP3, WAV, OGG">
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  style={{ display: 'none' }}
                />
                🎵 Добавить
              </label>
              <button className="record-audio-btn" onClick={() => setShowRecorder(true)}>
                <Mic size={16} />
                Записать
              </button>
              {uploading && <span className="uploading">Загрузка...</span>}
            </div>
          </div>
          <div className="attachments-content">
            
            {/* Модальное окно рекордера */}
            {showRecorder && (
              <div className="recorder-modal">
                <div className="recorder-modal-content">
                  <div className="recorder-header">
                    <h4>Запись голосового сообщения</h4>
                    <button onClick={() => setShowRecorder(false)}>
                      <X size={20} />
                    </button>
                  </div>
                  <AudioRecorder
                    onRecordingComplete={handleRecordingComplete}
                    onCancel={() => setShowRecorder(false)}
                  />
                </div>
              </div>
            )}
            
            {displayedAudios.length > 0 && (
              <div className="audio-list">
                {displayedAudios.map(att => {
                  const url = getAttachmentUrl(att.id);
                  const isEditing = editingNote.id === att.id;

                  return (
                    <div key={att.id} className="audio-item">
                      <audio controls src={url} />
                      <div className="audio-note">
                        {isEditing ? (
                          <>
                            <textarea
                              value={editingNote.text}
                              onChange={(e) => setEditingNote({ id: att.id, text: e.target.value })}
                              placeholder="Примечание..."
                            />
                            <div className="note-actions">
                              <button onClick={() => handleUpdateNote(att.id, editingNote.text)}>OK</button>
                              <button onClick={() => setEditingNote({ id: null, text: '' })}>X</button>
                            </div>
                          </>
                        ) : (
                          <>
                            <span onClick={() => setEditingNote({ id: att.id, text: att.note || '' })}>
                              {att.note || 'Добавить примечание'}
                            </span>
                            <button
                              className="delete-btn"
                              onClick={() => handleDeleteAttachment(att.id)}
                            >
                              <Trash2 size={12} />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
                {hiddenAudiosCount > 0 && (
                  <div className="audio-hidden-notice">
                    🚫 Скрыто {hiddenAudiosCount} аудиофайлов (лимит: {audioLimit})
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Модальное окно для увеличенного изображения */}
      {expandedImage && (
        <div className="image-modal" onClick={() => setExpandedImage(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <img src={expandedImage} alt="Full size" />
            <button className="modal-close" onClick={() => setExpandedImage(null)}>
              <X size={24} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// === Детали задачи ===

function TaskDetail({ id, onClose }) {
  const { tasks, categories, updateTask, deleteTask, loadSubtasks, createSubtask, updateSubtask, deleteSubtask } = useTasks();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(null);
  const [subtasks, setSubtasks] = useState([]);
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('');
  const [expandedSubtasks, setExpandedSubtasks] = useState(false);

  const task = tasks.find(t => t.id === id);

  React.useEffect(() => {
    if (task) {
      setEditData({
        ...task,
        priority: task.priority || 'medium',
        status: task.status || 'not_done'
      });
      loadSubtasks(task.id).then(setSubtasks);
    }
  }, [task, id, loadSubtasks]);

  if (!task) {
    return <div className="not-found">Задача не найдена</div>;
  }

  const handleSave = async () => {
    await updateTask(task.id, editData);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Удалить эту задачу?')) {
      await deleteTask(task.id);
      onClose();
    }
  };

  const handleAddSubtask = async () => {
    if (newSubtaskTitle.trim()) {
      await createSubtask(task.id, { title: newSubtaskTitle.trim(), is_completed: false });
      setNewSubtaskTitle('');
      const updated = await loadSubtasks(task.id);
      setSubtasks(updated);
    }
  };

  const handleToggleSubtask = async (subtask) => {
    await updateSubtask(task.id, subtask.id, { is_completed: !subtask.is_completed });
    const updated = await loadSubtasks(task.id);
    setSubtasks(updated);
  };

  const handleDeleteSubtask = async (subtaskId) => {
    if (window.confirm('Удалить эту подзадачу?')) {
      await deleteSubtask(task.id, subtaskId);
      const updated = await loadSubtasks(task.id);
      setSubtasks(updated);
    }
  };

  const category = categories.find(c => c.id === task.kategory_id);

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Цвета для приоритетов
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff4444';
      case 'medium': return '#ffaa00';
      case 'low': return '#44aa44';
      default: return '#888888';
    }
  };

  // Текстовые представления статуса
  const getStatusLabel = (status) => {
    switch (status) {
      case 'done': return 'Выполнена';
      case 'in_progress': return 'В процессе';
      case 'not_done': return 'Не выполнена';
      default: return status;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'done': return '#44aa44';
      case 'in_progress': return '#ffaa00';
      case 'not_done': return '#ff4444';
      default: return '#888888';
    }
  };

  const completedCount = subtasks.filter(s => s.is_completed).length;
  const totalCount = subtasks.length;

  if (isEditing && editData) {
    return (
      <div className="edit-form">
        <div className="form-header">
          <h3>Редактирование задачи</h3>
          <div className="form-actions">
            <button onClick={handleSave} className="save-btn">
              <Save size={16} /> Сохранить
            </button>
            <button onClick={() => setIsEditing(false)} className="cancel-btn">
              <X size={16} /> Отмена
            </button>
          </div>
        </div>
        <div className="form-body">
          <div className="form-group">
            <label>Название</label>
            <input
              type="text"
              value={editData.name}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Категория</label>
            <select
              value={editData.kategory_id || ''}
              onChange={(e) => setEditData({ ...editData, kategory_id: parseInt(e.target.value) || null })}
            >
              <option value="">Без категории</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Приоритет</label>
            <select
              value={editData.priority || 'medium'}
              onChange={(e) => setEditData({ ...editData, priority: e.target.value })}
            >
              <option value="high">Высокий</option>
              <option value="medium">Средний</option>
              <option value="low">Низкий</option>
            </select>
          </div>
          <div className="form-group">
            <label>Статус</label>
            <select
              value={editData.status || 'not_done'}
              onChange={(e) => setEditData({ ...editData, status: e.target.value })}
            >
              <option value="not_done">Не выполнена</option>
              <option value="in_progress">В процессе</option>
              <option value="done">Выполнена</option>
            </select>
          </div>
          <div className="form-group">
            <label>Срок выполнения</label>
            <input
              type="datetime-local"
              value={editData.data_time ? editData.data_time.split('T')[0] + 'T' + editData.data_time.split('T')[1]?.slice(0, 5) : ''}
              onChange={(e) => setEditData({ ...editData, data_time: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={editData.description || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              rows={5}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-view">
      <div className="detail-header">
        <h2>{task.name}</h2>
        <div className="detail-actions">
          <button onClick={() => setIsEditing(true)} className="edit-btn">
            <Edit size={16} /> Редактировать
          </button>
          <button onClick={handleDelete} className="delete-btn">
            <Trash2 size={16} /> Удалить
          </button>
          <button onClick={onClose} className="close-btn">
            <X size={16} /> Закрыть
          </button>
        </div>
      </div>
      <div className="detail-body">
        {category && (
          <div className="detail-row">
            <span className="label">Категория:</span>
            <span className="value">{category.name}</span>
          </div>
        )}
        <div className="detail-row">
          <span className="label">Приоритет:</span>
          <span className="value" style={{ color: getPriorityColor(task.priority || 'medium') }}>
            {task.priority === 'high' ? 'Высокий' : task.priority === 'low' ? 'Низкий' : 'Средний'}
          </span>
        </div>
        <div className="detail-row">
          <span className="label">Статус:</span>
          <span className="value" style={{ color: getStatusColor(task.status || 'not_done') }}>
            {getStatusLabel(task.status || 'not_done')}
          </span>
        </div>
        {task.data_time && (
          <div className="detail-row">
            <span className="label">Срок выполнения:</span>
            <span className="value">{formatDate(task.data_time)}</span>
          </div>
        )}
        {task.description && (
          <div className="detail-row">
            <span className="label">Описание:</span>
            <p className="description">{task.description}</p>
          </div>
        )}
        {task.created_at && (
          <div className="detail-row">
            <span className="label">Создана:</span>
            <span className="value">{formatDate(task.created_at)}</span>
          </div>
        )}

        {/* Подзадачи */}
        <div className="detail-row subtasks-section">
          <div className="subtasks-header" onClick={() => setExpandedSubtasks(!expandedSubtasks)}>
            <span className="label">
              <ChevronRight size={16} style={{ transform: expandedSubtasks ? 'rotate(90deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />
              Подзадачи ({completedCount}/{totalCount})
            </span>
          </div>

          {expandedSubtasks && (
            <div className="subtasks-list">
              {subtasks.length === 0 ? (
                <div className="no-subtasks">Нет подзадач</div>
              ) : (
                subtasks.map(subtask => (
                  <div key={subtask.id} className={`subtask-item ${subtask.is_completed ? 'completed' : ''}`}>
                    <input
                      type="checkbox"
                      checked={subtask.is_completed}
                      onChange={() => handleToggleSubtask(subtask)}
                    />
                    <span className="subtask-title">{subtask.title}</span>
                    {subtask.due_date && (
                      <span className="subtask-due">{formatDate(subtask.due_date)}</span>
                    )}
                    <button
                      className="delete-subtask-btn"
                      onClick={() => handleDeleteSubtask(subtask.id)}
                      title="Удалить подзадачу"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))
              )}

              {/* Форма добавления подзадачи */}
              <div className="add-subtask-form">
                <input
                  type="text"
                  placeholder="Новая подзадача..."
                  value={newSubtaskTitle}
                  onChange={(e) => setNewSubtaskTitle(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddSubtask()}
                />
                <button onClick={handleAddSubtask} className="add-subtask-btn">
                  <Plus size={14} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MainPanel;
