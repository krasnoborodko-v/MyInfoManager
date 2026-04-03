import React, { useState } from 'react';
import {
  FolderTree,
  FileText,
  CheckSquare,
  Calendar,
  Clock,
  Settings,
  Users,
  ExternalLink,
  Edit,
  Edit2,
  Trash2,
  Save,
  X,
  Check,
  Mic,
  ChevronRight,
  Plus,
  Star,
  Heart,
  Phone,
  Mail,
  Building,
  MapPin,
  Globe,
  Upload,
  Image,
  MessageCircle
} from 'lucide-react';
import { useResources, useNotes, useTasks, useContacts, useSettings, useFoldersTags } from '../hooks';
import AudioRecorder from './AudioRecorder';
import ContactPanel from './ContactPanel';
import { ContactDetailWrapper } from './ContactDetailWrapper';
import './MainPanel.css';

const sectionConfig = {
  resources: { icon: FolderTree, title: 'Ресурсы', description: 'Список информационных ресурсов' },
  notes: { icon: FileText, title: 'Заметки', description: 'Ваши заметки и идеи' },
  tasks: { icon: CheckSquare, title: 'Задачи', description: 'Список задач' },
  contacts: { icon: Users, title: 'Контакты', description: 'Управление контактами' },
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
            {selectedType === 'contact' && (
              <ContactDetailWrapper id={selectedId} onClose={() => onItemSelect(null)} />
            )}
          </div>
        ) : (
          activeSection === 'contacts' ? (
            <ContactPanel onItemSelect={onItemSelect} />
          ) : (
            <div className="placeholder-content">
              <div className="placeholder-box">
                <p>Выберите элемент в sidebar для просмотра и редактирования</p>
                <p className="hint">Используйте поиск для быстрого нахождения нужного элемента</p>
              </div>
            </div>
          )
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
  const [newSubtaskDescription, setNewSubtaskDescription] = useState('');
  const [newSubtaskDueDate, setNewSubtaskDueDate] = useState('');
  const [expandedSubtasks, setExpandedSubtasks] = useState(false);
  const [editingSubtaskId, setEditingSubtaskId] = useState(null);
  const [editingSubtaskData, setEditingSubtaskData] = useState(null);

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
      await createSubtask(task.id, { 
        title: newSubtaskTitle.trim(), 
        description: newSubtaskDescription.trim() || null,
        due_date: newSubtaskDueDate || null,
        is_completed: false 
      });
      setNewSubtaskTitle('');
      setNewSubtaskDescription('');
      setNewSubtaskDueDate('');
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

  const handleEditSubtask = (subtask) => {
    setEditingSubtaskId(subtask.id);
    setEditingSubtaskData({
      title: subtask.title,
      description: subtask.description || '',
      due_date: subtask.due_date ? subtask.due_date.slice(0, 16) : ''
    });
  };

  const handleSaveSubtask = async (subtaskId) => {
    await updateSubtask(task.id, subtaskId, editingSubtaskData);
    setEditingSubtaskId(null);
    setEditingSubtaskData(null);
    const updated = await loadSubtasks(task.id);
    setSubtasks(updated);
  };

  const handleCancelEditSubtask = () => {
    setEditingSubtaskId(null);
    setEditingSubtaskData(null);
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
                    {editingSubtaskId === subtask.id ? (
                      <div className="subtask-edit-form">
                        <input
                          type="text"
                          value={editingSubtaskData.title}
                          onChange={(e) => setEditingSubtaskData({...editingSubtaskData, title: e.target.value})}
                          placeholder="Название"
                        />
                        <textarea
                          value={editingSubtaskData.description || ''}
                          onChange={(e) => setEditingSubtaskData({...editingSubtaskData, description: e.target.value})}
                          placeholder="Описание"
                          rows={2}
                        />
                        <input
                          type="datetime-local"
                          value={editingSubtaskData.due_date || ''}
                          onChange={(e) => setEditingSubtaskData({...editingSubtaskData, due_date: e.target.value})}
                        />
                        <div className="subtask-actions">
                          <button onClick={() => handleSaveSubtask(subtask.id)} title="Сохранить">
                            <Check size={14} />
                          </button>
                          <button onClick={handleCancelEditSubtask} title="Отмена">
                            <X size={14} />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="subtask-view">
                        <div className="subtask-main">
                          <input
                            type="checkbox"
                            checked={subtask.is_completed}
                            onChange={() => handleToggleSubtask(subtask)}
                          />
                          <span className="subtask-title">{subtask.title}</span>
                        </div>
                        {subtask.description && (
                          <span className="subtask-description">{subtask.description}</span>
                        )}
                        {subtask.due_date && (
                          <span className="subtask-due">
                            <Calendar size={12} /> {formatDate(subtask.due_date)}
                          </span>
                        )}
                        <div className="subtask-buttons">
                          <button
                            className="edit-subtask-btn"
                            onClick={() => handleEditSubtask(subtask)}
                            title="Редактировать"
                          >
                            <Edit2 size={12} />
                          </button>
                          <button
                            className="delete-subtask-btn"
                            onClick={() => handleDeleteSubtask(subtask.id)}
                            title="Удалить"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}

              {/* Форма добавления подзадачи */}
              <div className="add-subtask-form">
                <input
                  type="text"
                  placeholder="Название подзадачи..."
                  value={newSubtaskTitle}
                  onChange={(e) => setNewSubtaskTitle(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddSubtask()}
                />
                <textarea
                  placeholder="Описание (необязательно)"
                  value={newSubtaskDescription}
                  onChange={(e) => setNewSubtaskDescription(e.target.value)}
                  rows={2}
                />
                <input
                  type="datetime-local"
                  value={newSubtaskDueDate}
                  onChange={(e) => setNewSubtaskDueDate(e.target.value)}
                  placeholder="Срок"
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

// === Детали контакта ===

function ContactDetail({ id, onClose }) {
  const { contacts, groups, updateContact, deleteContact, uploadPhoto, deletePhoto, getContactById } = useContacts();
  const [isEditing, setIsEditing] = useState(false);
  const [contact, setContact] = useState(null);
  const [editData, setEditData] = useState(null);

  // Загружаем контакт с фото
  React.useEffect(() => {
    const loadContact = async () => {
      const loaded = await getContactById(id);
      console.log('Loaded contact:', loaded);
      setContact(loaded);
    };
    loadContact();
  }, [id, getContactById]);
  
  console.log('MainPanel ContactDetail - contact.id:', contact?.id);
  console.log('MainPanel ContactDetail - contact.photo:', contact?.photo ? 'exists, length=' + (contact.photo.length || 'N/A') : 'null');
  console.log('MainPanel ContactDetail - contact.photo_type:', contact?.photo_type);

  React.useEffect(() => {
    if (contact) {
      setEditData({
        ...contact,
        birth_date: contact.birth_date ? contact.birth_date.slice(0, 10) : ''
      });
    }
  }, [contact]);

  if (!contact) {
    return <div className="not-found">Контакт не найден</div>;
  }

  const handleSave = async () => {
    await updateContact(contact.id, editData);
    // Обновляем контакт с сервера
    const updated = await getContactById(contact.id);
    setContact(updated);
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Удалить этот контакт?')) {
      await deleteContact(contact.id);
      onClose();
    }
  };

  const handleUploadPhoto = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadPhoto(contact.id, file);
      // Обновляем контакт с сервера
      const updated = await getContactById(contact.id);
      setContact(updated);
    }
  };

  const handleDeletePhoto = async () => {
    await deletePhoto(contact.id);
    // Обновляем контакт с сервера
    const updated = await getContactById(contact.id);
    setContact(updated);
  };

  const parseJson = (str) => {
    try {
      return str ? JSON.parse(str) : [];
    } catch {
      return [];
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Управление телефонами
  const handleAddPhone = () => {
    const phones = parseJson(editData.phones);
    const newPhones = [...phones, { type: 'mobile', value: '' }];
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  const handleUpdatePhone = (index, field, value) => {
    const phones = parseJson(editData.phones);
    const newPhones = phones.map((p, i) =>
      i === index ? { ...p, [field]: value } : p
    );
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  const handleDeletePhone = (index) => {
    const phones = parseJson(editData.phones);
    const newPhones = phones.filter((_, i) => i !== index);
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  // Управление Email
  const handleAddEmail = () => {
    const emails = parseJson(editData.emails);
    const newEmails = [...emails, { type: 'personal', value: '' }];
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  const handleUpdateEmail = (index, field, value) => {
    const emails = parseJson(editData.emails);
    const newEmails = emails.map((e, i) =>
      i === index ? { ...e, [field]: value } : e
    );
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  const handleDeleteEmail = (index) => {
    const emails = parseJson(editData.emails);
    const newEmails = emails.filter((_, i) => i !== index);
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  // Управление соцсетями
  const handleAddSocial = () => {
    const socials = parseJson(editData.socials);
    const newSocials = [...socials, { type: 'telegram', value: '' }];
    setEditData({ ...editData, socials: JSON.stringify(newSocials) });
  };

  const handleUpdateSocial = (index, field, value) => {
    const socials = parseJson(editData.socials);
    const newSocials = socials.map((s, i) =>
      i === index ? { ...s, [field]: value } : s
    );
    setEditData({ ...editData, socials: JSON.stringify(newSocials) });
  };

  const handleDeleteSocial = (index) => {
    const socials = parseJson(editData.socials);
    const newSocials = socials.filter((_, i) => i !== index);
    setEditData({ ...editData, socials: JSON.stringify(newSocials) });
  };

  return (
    <div className="contact-detail-overlay">
      <div className="contact-detail">
        <div className="detail-header">
          <h2>
            {contact.last_name} {contact.first_name} {contact.middle_name}
          </h2>
          <div className="header-actions">
            <button onClick={onClose} className="icon-btn" title="Закрыть">
              <X size={20} />
            </button>
            {!isEditing ? (
              <>
                <button onClick={() => setIsEditing(true)} className="icon-btn" title="Редактировать">
                  <Edit2 size={20} />
                </button>
                <button onClick={handleDelete} className="icon-btn danger" title="Удалить">
                  <Trash2 size={20} />
                </button>
              </>
            ) : (
              <>
                <button onClick={handleSave} className="icon-btn success" title="Сохранить">
                  <Save size={20} />
                </button>
                <button onClick={() => setIsEditing(false)} className="icon-btn" title="Отмена">
                  <X size={20} />
                </button>
              </>
            )}
          </div>
        </div>

        <div className="detail-content">
          {/* Фото */}
          <div className="detail-photo-section">
            {contact.photo ? (
              <div className="photo-preview">
                <img src={`data:${contact.photo_type || 'image/jpeg'};base64,${contact.photo}`} alt="Фото" />
                {isEditing && (
                  <button onClick={handleDeletePhoto} className="delete-photo-btn">
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ) : (
              <div className="photo-placeholder">
                <Image size={48} />
              </div>
            )}
            {isEditing && (
              <label className="upload-photo-btn">
                <Upload size={16} /> Загрузить фото
                <input type="file" accept="image/*" onChange={handleUploadPhoto} hidden />
              </label>
            )}
          </div>

          {/* Основная информация */}
          <div className="detail-section">
            <h3 className="section-title">Основная информация</h3>
            {isEditing ? (
              <div className="edit-grid">
                <input
                  placeholder="Фамилия"
                  value={editData.last_name}
                  onChange={(e) => setEditData({ ...editData, last_name: e.target.value })}
                />
                <input
                  placeholder="Имя"
                  value={editData.first_name}
                  onChange={(e) => setEditData({ ...editData, first_name: e.target.value })}
                />
                <input
                  placeholder="Отчество"
                  value={editData.middle_name || ''}
                  onChange={(e) => setEditData({ ...editData, middle_name: e.target.value })}
                />
                <select
                  value={editData.group_id || ''}
                  onChange={(e) => setEditData({ ...editData, group_id: e.target.value ? parseInt(e.target.value) : null })}
                >
                  <option value="">Без группы</option>
                  {groups.map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
                <input
                  type="date"
                  value={editData.birth_date || ''}
                  onChange={(e) => setEditData({ ...editData, birth_date: e.target.value })}
                />
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={editData.is_favorite}
                    onChange={(e) => setEditData({ ...editData, is_favorite: e.target.checked })}
                  />
                  <Heart size={16} fill={editData.is_favorite ? "currentColor" : "none"} /> Избранный
                </label>
              </div>
            ) : (
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Группа:</span>
                  <span className="info-value">{contact.group_name || 'Без группы'}</span>
                </div>
                {contact.birth_date && (
                  <div className="info-item">
                    <span className="info-label">Дата рождения:</span>
                    <span className="info-value">
                      <Calendar size={14} /> {formatDate(contact.birth_date)}
                    </span>
                  </div>
                )}
                {contact.is_favorite && (
                  <div className="info-item">
                    <span className="info-label">
                      <Star size={14} fill="currentColor" /> Избранный
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Телефоны */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title">
                <Phone size={18} /> Телефоны
              </h3>
              {isEditing && (
                <button onClick={handleAddPhone} className="add-btn">
                  <Plus size={16} />
                </button>
              )}
            </div>
            {isEditing ? (
              <div className="phones-edit">
                {parseJson(editData.phones).map((phone, index) => (
                  <div key={index} className="phone-edit-row">
                    <select
                      value={phone.type}
                      onChange={(e) => handleUpdatePhone(index, 'type', e.target.value)}
                    >
                      <option value="mobile">Мобильный</option>
                      <option value="work">Рабочий</option>
                      <option value="home">Домашний</option>
                      <option value="other">Другой</option>
                    </select>
                    <input
                      placeholder="+7..."
                      value={phone.value}
                      onChange={(e) => handleUpdatePhone(index, 'value', e.target.value)}
                    />
                    <button onClick={() => handleDeletePhone(index)} className="delete-field-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="phones-list">
                {parseJson(contact.phones).length > 0 ? (
                  parseJson(contact.phones).map((phone, index) => (
                    <div key={index} className="phone-item">
                      <span className="phone-type">{phone.type === 'mobile' ? 'Моб.' : phone.type === 'work' ? 'Рабочий' : phone.type === 'home' ? 'Дом.' : 'Др.'}</span>
                      <a href={`tel:${phone.value}`}>{phone.value}</a>
                    </div>
                  ))
                ) : (
                  <p className="no-data">Нет телефонов</p>
                )}
              </div>
            )}
          </div>

          {/* Email */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title">
                <Mail size={18} /> Email
              </h3>
              {isEditing && (
                <button onClick={handleAddEmail} className="add-btn">
                  <Plus size={16} />
                </button>
              )}
            </div>
            {isEditing ? (
              <div className="emails-edit">
                {parseJson(editData.emails).map((email, index) => (
                  <div key={index} className="email-edit-row">
                    <select
                      value={email.type}
                      onChange={(e) => handleUpdateEmail(index, 'type', e.target.value)}
                    >
                      <option value="personal">Личный</option>
                      <option value="work">Рабочий</option>
                      <option value="other">Другой</option>
                    </select>
                    <input
                      type="email"
                      placeholder="email@example.com"
                      value={email.value}
                      onChange={(e) => handleUpdateEmail(index, 'value', e.target.value)}
                    />
                    <button onClick={() => handleDeleteEmail(index)} className="delete-field-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="emails-list">
                {parseJson(contact.emails).length > 0 ? (
                  parseJson(contact.emails).map((email, index) => (
                    <div key={index} className="email-item">
                      <span className="email-type">{email.type === 'personal' ? 'Личный' : email.type === 'work' ? 'Рабочий' : 'Др.'}</span>
                      <a href={`mailto:${email.value}`}>{email.value}</a>
                    </div>
                  ))
                ) : (
                  <p className="no-data">Нет email</p>
                )}
              </div>
            )}
          </div>

          {/* Соцсети */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title">
                <MessageCircle size={18} /> Соцсети
              </h3>
              {isEditing && (
                <button onClick={handleAddSocial} className="add-btn">
                  <Plus size={16} />
                </button>
              )}
            </div>
            {isEditing ? (
              <div className="socials-edit">
                {parseJson(editData.socials).map((social, index) => (
                  <div key={index} className="social-edit-row">
                    <select
                      value={social.type}
                      onChange={(e) => handleUpdateSocial(index, 'type', e.target.value)}
                    >
                      <option value="telegram">Telegram</option>
                      <option value="whatsapp">WhatsApp</option>
                      <option value="viber">Viber</option>
                      <option value="vk">VK</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="other">Другой</option>
                    </select>
                    <input
                      placeholder="@username или ссылка"
                      value={social.value}
                      onChange={(e) => handleUpdateSocial(index, 'value', e.target.value)}
                    />
                    <button onClick={() => handleDeleteSocial(index)} className="delete-field-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="socials-list">
                {parseJson(contact.socials).length > 0 ? (
                  parseJson(contact.socials).map((social, index) => (
                    <div key={index} className="social-item">
                      <span className="social-type">{social.type}</span>
                      <a href={social.value.startsWith('http') ? social.value : `https://${social.type}.com/${social.value}`} target="_blank" rel="noopener noreferrer">
                        {social.value}
                      </a>
                    </div>
                  ))
                ) : (
                  <p className="no-data">Нет соцсетей</p>
                )}
              </div>
            )}
          </div>

          {/* Работа */}
          <div className="detail-section">
            <h3 className="section-title">
              <Building size={18} /> Место работы
            </h3>
            {isEditing ? (
              <div className="edit-row">
                <input
                  placeholder="Организация"
                  value={editData.company || ''}
                  onChange={(e) => setEditData({ ...editData, company: e.target.value })}
                />
                <input
                  placeholder="Должность"
                  value={editData.position || ''}
                  onChange={(e) => setEditData({ ...editData, position: e.target.value })}
                />
              </div>
            ) : (
              <div className="info-grid">
                {contact.company ? (
                  <div className="info-item">
                    <span className="info-label">Организация:</span>
                    <span className="info-value">{contact.company}</span>
                  </div>
                ) : (
                  <p className="no-data">Не указано</p>
                )}
                {contact.position && (
                  <div className="info-item">
                    <span className="info-label">Должность:</span>
                    <span className="info-value">{contact.position}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Адрес */}
          <div className="detail-section">
            <h3 className="section-title">
              <MapPin size={18} /> Адрес
            </h3>
            {isEditing ? (
              <textarea
                placeholder="Адрес"
                value={editData.address || ''}
                onChange={(e) => setEditData({ ...editData, address: e.target.value })}
                rows={2}
              />
            ) : (
              contact.address ? (
                <p className="info-value">{contact.address}</p>
              ) : (
                <p className="no-data">Не указан</p>
              )
            )}
          </div>

          {/* Сайт */}
          <div className="detail-section">
            <h3 className="section-title">
              <Globe size={18} /> Сайт
            </h3>
            {isEditing ? (
              <input
                placeholder="https://..."
                value={editData.website || ''}
                onChange={(e) => setEditData({ ...editData, website: e.target.value })}
              />
            ) : (
              contact.website ? (
                <a href={contact.website} target="_blank" rel="noopener noreferrer" className="info-value">
                  {contact.website}
                </a>
              ) : (
                <p className="no-data">Не указан</p>
              )
            )}
          </div>

          {/* Заметки */}
          <div className="detail-section">
            <h3 className="section-title">Заметки</h3>
            {isEditing ? (
              <textarea
                placeholder="Дополнительная информация"
                value={editData.notes || ''}
                onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
                rows={4}
              />
            ) : (
              contact.notes ? (
                <p className="notes-content">{contact.notes}</p>
              ) : (
                <p className="no-data">Нет заметок</p>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPanel;
