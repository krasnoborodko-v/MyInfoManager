import React, { useState } from 'react';
import {
  FolderTree,
  FileText,
  CheckSquare,
  Calendar,
  Clock,
  Settings,
  ChevronRight,
  ChevronDown,
  Plus,
  Trash2,
  Search
} from 'lucide-react';
import { useResources, useNotes, useTasks, useSettings, useFoldersTags } from '../hooks';
import './Sidebar.css';

const menuItems = [
  { id: 'resources', icon: FolderTree, label: 'Ресурсы' },
  { id: 'notes', icon: FileText, label: 'Заметки' },
  { id: 'tasks', icon: CheckSquare, label: 'Задачи' },
  { id: 'calendar', icon: Calendar, label: 'Календарь' },
  { id: 'planner', icon: Clock, label: 'Планировщик' },
  { id: 'settings', icon: Settings, label: 'Настройки' },
];

function Sidebar({ activeSection, onSectionChange, onItemSelect }) {
  const [expandedPanel, setExpandedPanel] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleIconClick = (sectionId) => {
    if (activeSection === sectionId) {
      setExpandedPanel(expandedPanel === sectionId ? null : sectionId);
    } else {
      onSectionChange(sectionId);
      setExpandedPanel(sectionId);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-icons">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          const isExpanded = expandedPanel === item.id;

          return (
            <button
              key={item.id}
              className={`icon-btn ${isActive ? 'active' : ''} ${isExpanded ? 'expanded' : ''}`}
              onClick={() => handleIconClick(item.id)}
              title={item.label}
            >
              <Icon size={24} />
            </button>
          );
        })}
      </div>

      {expandedPanel && (
        <div className="sidebar-panel">
          <div className="panel-header">
            <span>{menuItems.find(i => i.id === expandedPanel)?.label}</span>
            <button
              className="collapse-btn"
              onClick={() => setExpandedPanel(null)}
            >
              <ChevronRight size={16} />
            </button>
          </div>
          
          {/* Поиск для активных разделов */}
          {(expandedPanel === 'resources' || expandedPanel === 'notes' || expandedPanel === 'tasks') && (
            <div className="panel-search">
              <Search size={14} />
              <input
                type="text"
                placeholder="Поиск..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          )}
          
          <div className="panel-content">
            {expandedPanel === 'resources' && (
              <ResourcesPanel searchQuery={searchQuery} onItemSelect={onItemSelect} />
            )}
            {expandedPanel === 'notes' && (
              <NotesPanel searchQuery={searchQuery} onItemSelect={onItemSelect} />
            )}
            {expandedPanel === 'tasks' && (
              <TasksPanel searchQuery={searchQuery} onItemSelect={onItemSelect} />
            )}
            {expandedPanel === 'calendar' && <CalendarPanel />}
            {expandedPanel === 'planner' && <PlannerPanel />}
            {expandedPanel === 'settings' && <SettingsPanel />}
          </div>
        </div>
      )}
    </div>
  );
}

// === Компоненты панелей ===

// Компонент для рекурсивного отображения папок
function FolderNode({ folder, allFolders, notes, expandedFolders, onToggleFolder, onDeleteFolder, onItemSelect, formatDate, deleteNote }) {
  const children = allFolders.filter(f => f.parent_id === folder.id);
  const folderNotes = notes.filter(n => n.folder_id === folder.id);
  const isExpanded = expandedFolders[folder.id];

  return (
    <div className="folder-node">
      <div
        className="folder-header"
        onClick={() => onToggleFolder(folder.id)}
      >
        {children.length > 0 || folderNotes.length > 0 ? (
          isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />
        ) : (
          <span style={{ width: 14 }} />
        )}
        <FolderTree size={14} />
        <span className="folder-name">{folder.name}</span>
        {folderNotes.length > 0 && (
          <span className="folder-count">{folderNotes.length}</span>
        )}
        <button
          className="delete-btn"
          onClick={(e) => { e.stopPropagation(); onDeleteFolder(folder.id); }}
        >
          <Trash2 size={12} />
        </button>
      </div>
      {isExpanded && (
        <>
          {children.length > 0 && (
            <div className="folder-children">
              {children.map(child => (
                <FolderNode
                  key={child.id}
                  folder={child}
                  allFolders={allFolders}
                  notes={notes}
                  expandedFolders={expandedFolders}
                  onToggleFolder={onToggleFolder}
                  onDeleteFolder={onDeleteFolder}
                  onItemSelect={onItemSelect}
                  formatDate={formatDate}
                  deleteNote={deleteNote}
                />
              ))}
            </div>
          )}
          {folderNotes.length > 0 && (
            <div className="folder-notes">
              {folderNotes.map(note => (
                <div
                  key={note.id}
                  className="folder-note-leaf"
                  onClick={() => onItemSelect && onItemSelect({ type: 'note', id: note.id })}
                >
                  <FileText size={14} />
                  <span>{note.name}</span>
                  <span className="date">{formatDate(note.data_time)}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteNote(note.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ResourcesPanel({ searchQuery, onItemSelect }) {
  const {
    resources,
    categories,
    loading,
    error,
    searchResources,
    createResource,
    deleteResource,
    createCategory,
    deleteCategory,
  } = useResources();

  const [expandedCategories, setExpandedCategories] = useState([]);
  const [showNewCategory, setShowNewCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showNewResource, setShowNewResource] = useState(false);
  const [newResourceData, setNewResourceData] = useState({ name: '', url: '', description: '', kategory_id: null });

  // Поиск при изменении query
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchResources(searchQuery);
      } else {
        searchResources('');
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, searchResources]);

  const toggleCategory = (catId) => {
    setExpandedCategories(prev =>
      prev.includes(catId)
        ? prev.filter(id => id !== catId)
        : [...prev, catId]
    );
  };

  const handleCreateCategory = async () => {
    if (newCategoryName.trim()) {
      await createCategory(newCategoryName.trim());
      setNewCategoryName('');
      setShowNewCategory(false);
    }
  };

  const handleCreateResource = async () => {
    if (newResourceData.name.trim()) {
      await createResource(newResourceData);
      setNewResourceData({ name: '', url: '', description: '', kategory_id: null });
      setShowNewResource(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">Ошибка: {error}</div>;

  return (
    <div className="resources-panel">
      <div className="panel-actions">
        <button className="action-btn" onClick={() => setShowNewCategory(!showNewCategory)} title="Новая категория">
          <Plus size={14} /> Категория
        </button>
        <button className="action-btn" onClick={() => setShowNewResource(!showNewResource)} title="Новый ресурс">
          <Plus size={14} /> Ресурс
        </button>
      </div>

      {showNewCategory && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название категории"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateCategory()}
          />
          <button onClick={handleCreateCategory}>OK</button>
        </div>
      )}

      {showNewResource && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название"
            value={newResourceData.name}
            onChange={(e) => setNewResourceData({ ...newResourceData, name: e.target.value })}
          />
          <input
            type="text"
            placeholder="URL"
            value={newResourceData.url}
            onChange={(e) => setNewResourceData({ ...newResourceData, url: e.target.value })}
          />
          <select
            value={newResourceData.kategory_id || ''}
            onChange={(e) => setNewResourceData({ ...newResourceData, kategory_id: parseInt(e.target.value) || null })}
          >
            <option value="">Без категории</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          <textarea
            placeholder="Описание"
            value={newResourceData.description}
            onChange={(e) => setNewResourceData({ ...newResourceData, description: e.target.value })}
          />
          <button onClick={handleCreateResource}>OK</button>
        </div>
      )}

      <div className="tree-view">
        {categories.map(category => {
          const categoryResources = resources.filter(item => item.kategory_id === category.id);
          return (
            <div key={category.id} className="tree-item">
              <div
                className="tree-node"
                onClick={() => toggleCategory(category.id)}
              >
                {expandedCategories.includes(category.id)
                  ? <ChevronDown size={14} />
                  : <ChevronRight size={14} />
                }
                <FolderTree size={14} />
                <span>{category.name}</span>
                <span className="count">{categoryResources.length}</span>
                <button
                  className="delete-btn"
                  onClick={(e) => { e.stopPropagation(); deleteCategory(category.id); }}
                >
                  <Trash2 size={12} />
                </button>
              </div>
              {expandedCategories.includes(category.id) && (
                <div className="tree-children">
                  {categoryResources.map(item => (
                    <div 
                      key={item.id} 
                      className="tree-leaf"
                      onClick={() => onItemSelect && onItemSelect({ type: 'resource', id: item.id })}
                    >
                      <FileText size={14} />
                      <span className="resource-name">{item.name}</span>
                      {item.url && (
                        <a 
                          href={item.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="resource-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          🔗
                        </a>
                      )}
                      <button
                        className="delete-btn"
                        onClick={(e) => { e.stopPropagation(); deleteResource(item.id); }}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
        
        {/* Ресурсы без категории */}
        {resources.filter(r => !r.kategory_id).length > 0 && (
          <div className="tree-item">
            <div className="tree-node">
              <FolderTree size={14} />
              <span>Без категории</span>
            </div>
            <div className="tree-children">
              {resources.filter(r => !r.kategory_id).map(item => (
                <div 
                  key={item.id} 
                  className="tree-leaf"
                  onClick={() => onItemSelect && onItemSelect({ type: 'resource', id: item.id })}
                >
                  <FileText size={14} />
                  <span className="resource-name">{item.name}</span>
                  {item.url && (
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="resource-link"
                      onClick={(e) => e.stopPropagation()}
                    >
                      🔗
                    </a>
                  )}
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteResource(item.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function NotesPanel({ searchQuery, onItemSelect }) {
  const {
    notes,
    categories,
    loading,
    error,
    searchNotes,
    createNote,
    deleteNote,
    createCategory,
    deleteCategory,
    moveNoteToFolder,
  } = useNotes();
  
  const { folders, createFolder, deleteFolder, loadFolders } = useFoldersTags();

  const [expandedCategories, setExpandedCategories] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [showNewCategory, setShowNewCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showNewNote, setShowNewNote] = useState(false);
  const [newNoteData, setNewNoteData] = useState({ name: '', note_text: '', kategory_id: null, folder_id: null });
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [newFolderData, setNewFolderData] = useState({ name: '', parent_id: null, category_id: null });
  const [contextMenu, setContextMenu] = useState({ noteId: null, x: 0, y: 0 });
  const [showMoveMenu, setShowMoveMenu] = useState(false);

  // Загружаем папки для всех категорий
  React.useEffect(() => {
    if (categories.length > 0) {
      loadFolders(null, false);
    }
  }, [categories, loadFolders]);

  // Фильтруем папки по категориям
  const getFoldersForCategory = (categoryId) => {
    return folders.filter(f => f.note_category_id === categoryId && !f.parent_id);
  };

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchNotes(searchQuery);
      } else {
        searchNotes('');
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, searchNotes]);

  const toggleCategory = (catId) => {
    setExpandedCategories(prev =>
      prev.includes(catId)
        ? prev.filter(id => id !== catId)
        : [...prev, catId]
    );
  };

  const handleCreateCategory = async () => {
    if (newCategoryName.trim()) {
      await createCategory(newCategoryName.trim());
      setNewCategoryName('');
      setShowNewCategory(false);
    }
  };

  const handleCreateFolder = async () => {
    if (newFolderData.name.trim()) {
      await createFolder(newFolderData.name, newFolderData.parent_id, newFolderData.category_id);
      setNewFolderData({ name: '', parent_id: null, category_id: null });
      setShowNewFolder(false);
    }
  };

  const toggleFolder = (folderId) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderId]: !prev[folderId]
    }));
  };

  const handleContextMenu = (e, noteId) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ noteId, x: e.clientX, y: e.clientY });
    setShowMoveMenu(true);
  };

  const handleMoveNote = async (folderId) => {
    if (contextMenu.noteId) {
      await moveNoteToFolder(contextMenu.noteId, folderId);
      setContextMenu({ noteId: null, x: 0, y: 0 });
      setShowMoveMenu(false);
    }
  };

  const handleCreateNote = async () => {
    if (newNoteData.name.trim()) {
      await createNote({
        ...newNoteData,
        data_time: new Date().toISOString()
      });
      setNewNoteData({ name: '', note_text: '', kategory_id: null });
      setShowNewNote(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">Ошибка: {error}</div>;

  return (
    <div className="notes-panel">
      <div className="panel-actions">
        <button className="action-btn" onClick={() => setShowNewCategory(!showNewCategory)}>
          <Plus size={14} /> Категория
        </button>
        <button className="action-btn" onClick={() => setShowNewFolder(!showNewFolder)}>
          <Plus size={14} /> Папка
        </button>
        <button className="action-btn" onClick={() => setShowNewNote(!showNewNote)}>
          <Plus size={14} /> Заметка
        </button>
      </div>

      {showNewFolder && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название папки"
            value={newFolderData.name}
            onChange={(e) => setNewFolderData({ ...newFolderData, name: e.target.value })}
          />
          <select
            value={newFolderData.category_id || ''}
            onChange={(e) => setNewFolderData({ ...newFolderData, category_id: parseInt(e.target.value) || null })}
          >
            <option value="">Выберите категорию</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          <select
            value={newFolderData.parent_id || ''}
            onChange={(e) => setNewFolderData({ ...newFolderData, parent_id: parseInt(e.target.value) || null })}
          >
            <option value="">Без родительской папки</option>
            {folders.filter(f => !f.parent_id).map(f => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
          <button onClick={handleCreateFolder}>OK</button>
        </div>
      )}

      {showNewCategory && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название категории"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateCategory()}
          />
          <button onClick={handleCreateCategory}>OK</button>
        </div>
      )}

      {showNewNote && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название"
            value={newNoteData.name}
            onChange={(e) => setNewNoteData({ ...newNoteData, name: e.target.value })}
          />
          <select
            value={newNoteData.kategory_id || ''}
            onChange={(e) => setNewNoteData({ ...newNoteData, kategory_id: parseInt(e.target.value) || null, folder_id: null })}
          >
            <option value="">Без категории</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          {newNoteData.kategory_id && getFoldersForCategory(newNoteData.kategory_id).length > 0 && (
            <select
              value={newNoteData.folder_id || ''}
              onChange={(e) => setNewNoteData({ ...newNoteData, folder_id: parseInt(e.target.value) || null })}
            >
              <option value="">Без папки</option>
              {getFoldersForCategory(newNoteData.kategory_id).map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          )}
          <textarea
            placeholder="Текст заметки"
            value={newNoteData.note_text}
            onChange={(e) => setNewNoteData({ ...newNoteData, note_text: e.target.value })}
          />
          <button onClick={handleCreateNote}>OK</button>
        </div>
      )}

      {/* Дерево папок удалено - папки теперь внутри категорий */}

      <div className="accordion">
        {categories.length > 0 ? (
          categories.map(category => {
            const categoryNotes = notes.filter(n => n.kategory_id === category.id && !n.folder_id);
            const categoryFolders = getFoldersForCategory(category.id);
            
            return (
              <div key={category.id} className="accordion-item">
                <div
                  className="accordion-header"
                  onClick={() => toggleCategory(category.id)}
                >
                  {expandedCategories.includes(category.id)
                    ? <ChevronDown size={14} />
                    : <ChevronRight size={14} />
                  }
                  <FolderTree size={14} />
                  <span>{category.name}</span>
                  <span className="count">{categoryNotes.length + categoryFolders.length}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteCategory(category.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
                {expandedCategories.includes(category.id) && (
                  <div className="accordion-content">
                    {/* Папки внутри категории */}
                    {categoryFolders.length > 0 && (
                      <div className="category-folders">
                        {categoryFolders.map(folder => (
                          <FolderNode
                            key={folder.id}
                            folder={folder}
                            allFolders={folders}
                            notes={notes}
                            expandedFolders={expandedFolders}
                            onToggleFolder={toggleFolder}
                            onDeleteFolder={deleteFolder}
                            onItemSelect={onItemSelect}
                            formatDate={formatDate}
                            deleteNote={deleteNote}
                          />
                        ))}
                      </div>
                    )}
                    
                    {/* Заметки без папки */}
                    {categoryNotes.map(note => (
                      <div
                        key={note.id}
                        className="accordion-leaf"
                        onClick={() => onItemSelect && onItemSelect({ type: 'note', id: note.id })}
                        onContextMenu={(e) => handleContextMenu(e, note.id)}
                      >
                        <span>{note.name}</span>
                        <span className="date">{formatDate(note.data_time)}</span>
                        <button
                          className="delete-btn"
                          onClick={(e) => { e.stopPropagation(); deleteNote(note.id); }}
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="no-categories">Нет категорий. Создайте первую категорию.</div>
        )}

        {/* Заметки без категории */}
        {notes.filter(n => !n.kategory_id).length > 0 && (
          <div className="accordion-item">
            <div className="accordion-header">
              <FileText size={14} />
              <span>Без категории</span>
              <span className="count">{notes.filter(n => !n.kategory_id).length}</span>
            </div>
            <div className="accordion-content">
              {notes.filter(n => !n.kategory_id).map(note => (
                <div 
                  key={note.id} 
                  className="accordion-leaf"
                  onClick={() => onItemSelect && onItemSelect({ type: 'note', id: note.id })}
                >
                  <span>{note.name}</span>
                  <span className="date">{formatDate(note.data_time)}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteNote(note.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Контекстное меню для перемещения заметки */}
      {showMoveMenu && contextMenu.noteId && (
        <div 
          className="context-menu-overlay"
          onClick={() => { setContextMenu({ noteId: null, x: 0, y: 0 }); setShowMoveMenu(false); }}
        >
          <div 
            className="context-menu"
            style={{ left: contextMenu.x, top: contextMenu.y }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="context-menu-header">Переместить в папку</div>
            <button 
              className="context-menu-item"
              onClick={() => handleMoveNote(null)}
            >
              📁 Без папки
            </button>
            {folders
              .filter(f => f.note_category_id === notes.find(n => n.id === contextMenu.noteId)?.kategory_id)
              .map(folder => (
                <button
                  key={folder.id}
                  className="context-menu-item"
                  onClick={() => handleMoveNote(folder.id)}
                >
                  📁 {folder.name}
                </button>
              ))
            }
            <div className="context-menu-divider"></div>
            <button 
              className="context-menu-item cancel"
              onClick={() => { setContextMenu({ noteId: null, x: 0, y: 0 }); setShowMoveMenu(false); }}
            >
              Отмена
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function TasksPanel({ searchQuery, onItemSelect }) {
  const {
    tasks,
    categories,
    loading,
    error,
    searchTasks,
    createTask,
    updateTask,
    deleteTask,
    createCategory,
    deleteCategory,
  } = useTasks();

  const [expandedCategories, setExpandedCategories] = useState([]);
  const [showNewCategory, setShowNewCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [showNewTask, setShowNewTask] = useState(false);
  const [newTaskData, setNewTaskData] = useState({ name: '', kategory_id: null });

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchTasks(searchQuery);
      } else {
        searchTasks('');
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, searchTasks]);

  const toggleCategory = (catId) => {
    setExpandedCategories(prev =>
      prev.includes(catId)
        ? prev.filter(id => id !== catId)
        : [...prev, catId]
    );
  };

  const handleCreateCategory = async () => {
    if (newCategoryName.trim()) {
      await createCategory(newCategoryName.trim());
      setNewCategoryName('');
      setShowNewCategory(false);
    }
  };

  const handleCreateTask = async () => {
    if (newTaskData.name.trim()) {
      await createTask(newTaskData);
      setNewTaskData({ name: '', kategory_id: null });
      setShowNewTask(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
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

  // Цвета для статусов
  const getStatusBorderColor = (status) => {
    switch (status) {
      case 'done': return '#44aa44';
      case 'in_progress': return '#ffaa00';
      case 'not_done': return '#ff4444';
      default: return '#888888';
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">Ошибка: {error}</div>;

  return (
    <div className="tasks-panel">
      <div className="panel-actions">
        <button className="action-btn" onClick={() => setShowNewCategory(!showNewCategory)}>
          <Plus size={14} /> Категория
        </button>
        <button className="action-btn" onClick={() => setShowNewTask(!showNewTask)}>
          <Plus size={14} /> Задача
        </button>
      </div>

      {showNewCategory && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название категории"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateCategory()}
          />
          <button onClick={handleCreateCategory}>OK</button>
        </div>
      )}

      {showNewTask && (
        <div className="new-item-form">
          <input
            type="text"
            placeholder="Название задачи"
            value={newTaskData.name}
            onChange={(e) => setNewTaskData({ ...newTaskData, name: e.target.value })}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateTask()}
          />
          <select
            value={newTaskData.kategory_id || ''}
            onChange={(e) => setNewTaskData({ ...newTaskData, kategory_id: parseInt(e.target.value) || null })}
          >
            <option value="">Без категории</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          <button onClick={handleCreateTask}>OK</button>
        </div>
      )}

      <div className="accordion">
        {categories.map(category => {
          const categoryTasks = tasks.filter(t => t.kategory_id === category.id);
          return (
            <div key={category.id} className="accordion-item">
              <div
                className="accordion-header"
                onClick={() => toggleCategory(category.id)}
              >
                {expandedCategories.includes(category.id)
                  ? <ChevronDown size={14} />
                  : <ChevronRight size={14} />
                }
                <CheckSquare size={14} />
                <span>{category.name}</span>
                <span className="count">{categoryTasks.length}</span>
                <button
                  className="delete-btn"
                  onClick={(e) => { e.stopPropagation(); deleteCategory(category.id); }}
                >
                  <Trash2 size={12} />
                </button>
              </div>
              {expandedCategories.includes(category.id) && (
                <div className="accordion-content">
                  {categoryTasks.map(task => (
                    <div
                      key={task.id}
                      className="accordion-leaf task-item"
                      style={{ borderLeft: `3px solid ${getStatusBorderColor(task.status)}` }}
                      onClick={() => onItemSelect && onItemSelect({ type: 'task', id: task.id })}
                    >
                      <span className="task-name">{task.name}</span>
                      <span
                        className="priority-indicator"
                        style={{ color: getPriorityColor(task.priority) }}
                        title={`Приоритет: ${task.priority}`}
                      >
                        ●
                      </span>
                      <span className="date">{formatDate(task.data_time)}</span>
                      <button
                        className="delete-btn"
                        onClick={(e) => { e.stopPropagation(); deleteTask(task.id); }}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {/* Задачи без категории */}
        {tasks.filter(t => !t.kategory_id).length > 0 && (
          <div className="accordion-item">
            <div className="accordion-header">
              <CheckSquare size={14} />
              <span>Без категории</span>
              <span className="count">{tasks.filter(t => !t.kategory_id).length}</span>
            </div>
            <div className="accordion-content">
              {tasks.filter(t => !t.kategory_id).map(task => (
                <div
                  key={task.id}
                  className="accordion-leaf task-item"
                  style={{ borderLeft: `3px solid ${getStatusBorderColor(task.status)}` }}
                  onClick={() => onItemSelect && onItemSelect({ type: 'task', id: task.id })}
                >
                  <span className="task-name">{task.name}</span>
                  <span
                    className="priority-indicator"
                    style={{ color: getPriorityColor(task.priority) }}
                    title={`Приоритет: ${task.priority}`}
                  >
                    ●
                  </span>
                  <span className="date">{formatDate(task.data_time)}</span>
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteTask(task.id); }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CalendarPanel() {
  const today = new Date();
  const currentMonth = today.toLocaleString('ru', { month: 'long', year: 'numeric' });

  return (
    <div className="calendar-view">
      <div className="calendar-header">{currentMonth}</div>
      <div className="calendar-grid">
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map(day => (
          <div key={day} className="calendar-day-header">{day}</div>
        ))}
        {Array.from({ length: 35 }, (_, i) => {
          const dayNum = i - 2;
          const isToday = dayNum === today.getDate();
          const isValidDay = dayNum > 0 && dayNum <= 31;
          return (
            <div
              key={i}
              className={`calendar-cell ${isToday ? 'today' : ''} ${!isValidDay ? 'empty' : ''}`}
            >
              {isValidDay ? dayNum : ''}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PlannerPanel() {
  return (
    <div className="planner-view">
      <div className="planner-header">На сегодня</div>
      <div className="planner-item">
        <span className="time">09:00</span>
        <span className="event">Планёрка</span>
      </div>
      <div className="planner-item">
        <span className="time">11:00</span>
        <span className="event">Разработка</span>
      </div>
    </div>
  );
}

function SettingsPanel() {
  const { getSetting, updateSetting, settings, loading } = useSettings();
  const [serverAvailable, setServerAvailable] = useState(null);
  const [audioLimit, setAudioLimit] = useState(5);
  const [syncEnabled, setSyncEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  React.useEffect(() => {
    // Проверка доступности сервера
    const checkServer = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/health`);
        setServerAvailable(response.ok);
      } catch {
        setServerAvailable(false);
      }
    };
    checkServer();
  }, []);

  React.useEffect(() => {
    // Загрузка текущих настроек
    const limit = getSetting('audio_limit', '5');
    const sync = getSetting('sync_enabled', 'true');
    const notify = getSetting('notifications_enabled', 'true');
    setAudioLimit(parseInt(limit) || 5);
    setSyncEnabled(sync === 'true' || sync === '1');
    setNotificationsEnabled(notify === 'true' || notify === '1');
  }, [settings, getSetting]);

  const handleAudioLimitChange = async (e) => {
    const newValue = parseInt(e.target.value);
    if (newValue >= 1 && newValue <= 100) {
      setAudioLimit(newValue);
      await updateSetting('audio_limit', newValue.toString());
    }
  };

  const handleSyncChange = async (e) => {
    const newValue = e.target.checked;
    setSyncEnabled(newValue);
    await updateSetting('sync_enabled', newValue ? 'true' : 'false');
  };

  const handleNotificationsChange = async (e) => {
    const newValue = e.target.checked;
    setNotificationsEnabled(newValue);
    await updateSetting('notifications_enabled', newValue ? 'true' : 'false');
  };

  return (
    <div className="settings-view">
      <div className="settings-header">Настройки</div>

      <div className="settings-item">
        <span>Сервер бэкенда</span>
        <span className={`status ${serverAvailable ? 'ok' : 'error'}`}>
          {serverAvailable === null ? 'Проверка...' : serverAvailable ? 'Доступен' : 'Недоступен'}
        </span>
      </div>

      <div className="settings-item">
        <label htmlFor="audio-limit">Лимит аудио в заметке:</label>
        <input
          id="audio-limit"
          type="number"
          min="1"
          max="100"
          value={audioLimit}
          onChange={handleAudioLimitChange}
          disabled={loading}
        />
      </div>

      <div className="settings-item">
        <span>Синхронизация</span>
        <input 
          type="checkbox" 
          checked={syncEnabled}
          onChange={handleSyncChange}
          disabled={loading}
        />
      </div>

      <div className="settings-item">
        <span>Уведомления</span>
        <input 
          type="checkbox"
          checked={notificationsEnabled}
          onChange={handleNotificationsChange}
          disabled={loading}
        />
      </div>
    </div>
  );
}

export default Sidebar;
