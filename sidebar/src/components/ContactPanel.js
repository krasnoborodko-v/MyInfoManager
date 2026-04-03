import React, { useState, useCallback } from 'react';
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  Star,
  Search,
  X,
  Save,
  Upload,
  Image,
  Phone,
  Mail,
  MapPin,
  Building,
  Briefcase,
  Calendar,
  Globe,
  MessageCircle,
  Heart,
  Filter,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { useContacts } from '../hooks';
import './ContactPanel.css';

const sectionConfig = {
  icon: Users,
  title: 'Контакты',
  description: 'Управление контактами'
};

/**
 * Компонент раздела "Контакты".
 */
export function ContactPanel({ onItemSelect }) {
  const {
    contacts,
    groups,
    loading,
    error,
    loadContacts,
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
    deletePhoto
  } = useContacts();

  const [selectedContact, setSelectedContact] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [newGroupData, setNewGroupData] = useState({ name: '', color: '#008888' });
  const [editingGroupId, setEditingGroupId] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Фильтрация контактов
  const filteredContacts = contacts.filter(contact => {
    if (selectedGroup && contact.group_id !== selectedGroup) return false;
    if (showFavoritesOnly && !contact.is_favorite) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const fullName = `${contact.last_name} ${contact.first_name} ${contact.middle_name}`.toLowerCase();
      return fullName.includes(query);
    }
    return true;
  });

  // Группировка контактов
  const contactsByGroup = filteredContacts.reduce((acc, contact) => {
    const groupId = contact.group_id || 'no-group';
    if (!acc[groupId]) acc[groupId] = [];
    acc[groupId].push(contact);
    return acc;
  }, {});

  // Создание контакта
  const handleCreate = () => {
    setEditData({
      first_name: '',
      last_name: '',
      middle_name: '',
      group_id: null,
      phones: JSON.stringify([]),
      emails: JSON.stringify([]),
      address: '',
      company: '',
      position: '',
      birth_date: '',
      socials: JSON.stringify([]),
      website: '',
      is_favorite: false,
      notes: ''
    });
    setIsCreating(true);
    setIsEditing(true);
  };

  // Сохранение контакта
  const handleSave = async () => {
    try {
      if (isCreating) {
        await createContact(editData);
        // Перезагружаем контакты чтобы получить актуальные данные с group_name
        await loadContacts();
      } else {
        await updateContact(selectedContact.id, editData);
        const updatedContacts = await loadContacts();
        // Находим обновлённый контакт
        const updated = updatedContacts.find(c => c.id === selectedContact.id);
        if (updated) {
          setSelectedContact(updated);
        }
      }
      setIsEditing(false);
      setIsCreating(false);
      setEditData(null);
    } catch (err) {
      console.error('Error saving contact:', err);
    }
  };

  // Удаление контакта
  const handleDelete = async () => {
    if (window.confirm('Удалить этот контакт?')) {
      await deleteContact(selectedContact.id);
      setSelectedContact(null);
    }
  };

  // Переключение избранного
  const handleToggleFavorite = async (contactId, e) => {
    e.stopPropagation();
    await toggleFavorite(contactId);
  };

  // Загрузка фото
  const handleUploadPhoto = async (e) => {
    const file = e.target.files[0];
    if (file && selectedContact) {
      await uploadPhoto(selectedContact.id, file);
      // Перезагружаем контакты
      await loadContacts();
      // Загружаем контакт с фото
      const updated = await getContactById(selectedContact.id);
      if (updated) {
        setSelectedContact(updated);
      }
    }
  };

  // Удаление фото
  const handleDeletePhoto = async () => {
    if (selectedContact) {
      await deletePhoto(selectedContact.id);
      // Перезагружаем контакты
      await loadContacts();
      // Загружаем контакт без фото
      const updated = await getContactById(selectedContact.id);
      if (updated) {
        setSelectedContact(updated);
      }
    }
  };

  // Открытие редактирования
  const handleEdit = () => {
    if (selectedContact) {
      setEditData({
        ...selectedContact,
        birth_date: selectedContact.birth_date ? selectedContact.birth_date.slice(0, 10) : ''
      });
      setIsEditing(true);
    }
  };

  // Отмена редактирования
  const handleCancel = () => {
    setIsEditing(false);
    setIsCreating(false);
    setEditData(null);
  };

  // Управление группами
  const handleCreateGroup = async () => {
    if (newGroupData.name.trim()) {
      await createGroup(newGroupData.name, newGroupData.color);
      setNewGroupData({ name: '', color: '#008888' });
      setShowGroupModal(false);
    }
  };

  const handleUpdateGroup = async (groupId, data) => {
    await updateGroup(groupId, data);
    setEditingGroupId(null);
  };

  const handleDeleteGroup = async (groupId) => {
    if (window.confirm('Удалить эту группу? Контакты не будут удалены.')) {
      await deleteGroup(groupId);
      if (selectedGroup === groupId) setSelectedGroup(null);
    }
  };

  // Получение имени группы
  const getGroupName = (groupId) => {
    const group = groups.find(g => g.id == groupId);
    return group ? group.name : 'Без группы';
  };

  // Получение цвета группы
  const getGroupColor = (groupId) => {
    const group = groups.find(g => g.id == groupId);
    return group ? group.color : '#888888';
  };

  // Парсинг JSON полей
  const parseJson = (str) => {
    try {
      return str ? JSON.parse(str) : [];
    } catch {
      return [];
    }
  };

  // Форматирование даты рождения
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading && contacts.length === 0) {
    return (
      <div className="contact-panel">
        <div className="placeholder-content">
          <div className="placeholder">
            <Users size={64} />
            <p>Загрузка контактов...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="contact-panel">
        <div className="placeholder-content">
          <div className="placeholder">
            <Users size={64} />
            <p className="error">Ошибка: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-panel">
      {/* Заголовок */}
      <div className="section-header">
        <Users size={32} />
        <h1>{sectionConfig.title}</h1>
        <button
          className={`icon-btn ${showFavoritesOnly ? 'active' : ''}`}
          onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
          title="Избранные"
        >
          <Star size={20} fill={showFavoritesOnly ? "currentColor" : "none"} />
        </button>
        <button
          className="icon-btn"
          onClick={() => setShowFilters(!showFilters)}
          title="Фильтры"
        >
          <Filter size={20} />
        </button>
        <button
          className="icon-btn"
          onClick={handleCreate}
          title="Добавить контакт"
        >
          <Plus size={20} />
        </button>
      </div>

      <p className="section-description">{sectionConfig.description}</p>

      {/* Фильтры */}
      {showFilters && (
        <div className="filters-section">
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Поиск контактов..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="clear-btn">
                <X size={16} />
              </button>
            )}
          </div>

          <div className="group-filters">
            <button
              className={`group-filter-btn ${selectedGroup === null ? 'active' : ''}`}
              onClick={() => setSelectedGroup(null)}
            >
              Все
            </button>
            {groups.map(group => (
              <button
                key={group.id}
                className={`group-filter-btn ${selectedGroup === group.id ? 'active' : ''}`}
                onClick={() => setSelectedGroup(group.id)}
                style={{ borderColor: group.color }}
              >
                {group.name}
              </button>
            ))}
            <button
              className="icon-btn small"
              onClick={() => setShowGroupModal(true)}
              title="Добавить группу"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Список контактов */}
      <div className="contact-list">
        {filteredContacts.length === 0 ? (
          <div className="no-contacts">
            <Users size={48} />
            <p>Контакты не найдены</p>
          </div>
        ) : (
          Object.entries(contactsByGroup).map(([groupId, groupContacts]) => (
            <div key={groupId} className="contact-group-section">
              <div className="contact-group-header">
                <span
                  className="group-color-indicator"
                  style={{ backgroundColor: getGroupColor(groupId) }}
                />
                <span className="group-name">{getGroupName(groupId)}</span>
                <span className="contact-count">{groupContacts.length}</span>
                {groupId !== 'no-group' && (
                  <div className="group-actions">
                    <button
                      className="icon-btn small"
                      onClick={() => handleUpdateGroup(groupId, { name: prompt('Новое название группы:', getGroupName(groupId)) })}
                    >
                      <Edit2 size={12} />
                    </button>
                    <button
                      className="icon-btn small"
                      onClick={() => handleDeleteGroup(groupId)}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                )}
              </div>
              <div className="contacts-grid">
                {groupContacts.map(contact => (
                  <div
                    key={contact.id}
                    className={`contact-card ${selectedContact?.id === contact.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedContact(contact);
                      if (onItemSelect) {
                        onItemSelect({ type: 'contact', id: contact.id });
                      }
                    }}
                  >
                    <div className="contact-card-header">
                      <div className="contact-photo-wrapper">
                        {contact.photo ? (
                          <img
                            src={`data:image/jpeg;base64,${contact.photo}`}
                            alt={contact.first_name}
                            className="contact-photo"
                          />
                        ) : (
                          <div className="contact-photo-placeholder">
                            {contact.first_name[0]}{contact.last_name[0]}
                          </div>
                        )}
                      </div>
                      <button
                        className={`favorite-btn ${contact.is_favorite ? 'active' : ''}`}
                        onClick={(e) => handleToggleFavorite(contact.id, e)}
                      >
                        <Star size={16} fill={contact.is_favorite ? "currentColor" : "none"} />
                      </button>
                    </div>
                    <div className="contact-card-body">
                      <h3 className="contact-name">
                        {contact.last_name} {contact.first_name} {contact.middle_name}
                      </h3>
                      {contact.company && (
                        <p className="contact-company">{contact.company}</p>
                      )}
                      {contact.position && (
                        <p className="contact-position">{contact.position}</p>
                      )}
                      <div className="contact-info-mini">
                        {contact.phones && parseJson(contact.phones).length > 0 && (
                          <span className="mini-info">
                            <Phone size={12} /> {parseJson(contact.phones).length}
                          </span>
                        )}
                        {contact.emails && parseJson(contact.emails).length > 0 && (
                          <span className="mini-info">
                            <Mail size={12} /> {parseJson(contact.emails).length}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Детали контакта */}
      {selectedContact && !isCreating && !isEditing && (
        <ContactDetail
          contact={selectedContact}
          groups={groups}
          isEditing={isEditing}
          editData={editData}
          setEditData={setEditData}
          onEdit={handleEdit}
          onSave={handleSave}
          onCancel={handleCancel}
          onDelete={handleDelete}
          onUploadPhoto={handleUploadPhoto}
          onDeletePhoto={handleDeletePhoto}
          parseJson={parseJson}
          formatDate={formatDate}
        />
      )}

      {/* Форма создания/редактирования */}
      {(isCreating || isEditing) && editData && (
        <ContactForm
          isCreating={isCreating}
          editData={editData}
          setEditData={setEditData}
          groups={groups}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}

      {/* Модальное окно группы */}
      {showGroupModal && (
        <div className="modal-overlay" onClick={() => setShowGroupModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Новая группа</h2>
            <input
              type="text"
              placeholder="Название группы"
              value={newGroupData.name}
              onChange={(e) => setNewGroupData({ ...newGroupData, name: e.target.value })}
            />
            <div className="color-picker">
              <label>Цвет:</label>
              <input
                type="color"
                value={newGroupData.color}
                onChange={(e) => setNewGroupData({ ...newGroupData, color: e.target.value })}
              />
            </div>
            <div className="modal-actions">
              <button onClick={handleCreateGroup} className="btn-primary">
                <Save size={16} /> Создать
              </button>
              <button onClick={() => setShowGroupModal(false)} className="btn-secondary">
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Детали контакта
export function ContactDetail({
  contact,
  groups,
  isEditing,
  editData,
  setEditData,
  onEdit,
  onSave,
  onCancel,
  onDelete,
  onUploadPhoto,
  onDeletePhoto,
  parseJson,
  formatDate
}) {
  const [expandedPhones, setExpandedPhones] = useState(false);
  const [expandedEmails, setExpandedEmails] = useState(false);
  const [expandedSocials, setExpandedSocials] = useState(false);

  const phones = parseJson(contact.phones);
  const emails = parseJson(contact.emails);
  const socials = parseJson(contact.socials);

  const handleAddPhone = () => {
    const newPhones = [...phones, { type: 'mobile', value: '' }];
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  const handleUpdatePhone = (index, value) => {
    const newPhones = phones.map((p, i) => i === index ? { ...p, value } : p);
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  const handleDeletePhone = (index) => {
    const newPhones = phones.filter((_, i) => i !== index);
    setEditData({ ...editData, phones: JSON.stringify(newPhones) });
  };

  const handleAddEmail = () => {
    const newEmails = [...emails, { type: 'personal', value: '' }];
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  const handleUpdateEmail = (index, value) => {
    const newEmails = emails.map((e, i) => i === index ? { ...e, value } : e);
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  const handleDeleteEmail = (index) => {
    const newEmails = emails.filter((_, i) => i !== index);
    setEditData({ ...editData, emails: JSON.stringify(newEmails) });
  };

  return (
    <div className="contact-detail-overlay">
      <div className="contact-detail">
        <div className="detail-header">
          <h2>
            {contact.last_name} {contact.first_name} {contact.middle_name}
          </h2>
          <div className="header-actions">
            <button onClick={onCancel} className="icon-btn" title="Закрыть">
              <X size={20} />
            </button>
            {!isEditing ? (
              <>
                <button onClick={onEdit} className="icon-btn" title="Редактировать">
                  <Edit2 size={20} />
                </button>
                <button onClick={onDelete} className="icon-btn danger" title="Удалить">
                  <Trash2 size={20} />
                </button>
              </>
            ) : (
              <>
                <button onClick={onSave} className="icon-btn success" title="Сохранить">
                  <Save size={20} />
                </button>
                <button onClick={onCancel} className="icon-btn" title="Отмена">
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
                  <button onClick={onDeletePhoto} className="delete-photo-btn">
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
                <input type="file" accept="image/*" onChange={onUploadPhoto} hidden />
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
                  value={editData.middle_name}
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
                  placeholder="Дата рождения"
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
                {phones.map((phone, index) => (
                  <div key={index} className="phone-edit-row">
                    <select
                      value={phone.type}
                      onChange={(e) => {
                        const newPhones = phones.map((p, i) =>
                          i === index ? { ...p, type: e.target.value } : p
                        );
                        setEditData({ ...editData, phones: JSON.stringify(newPhones) });
                      }}
                    >
                      <option value="mobile">Мобильный</option>
                      <option value="work">Рабочий</option>
                      <option value="home">Домашний</option>
                      <option value="other">Другой</option>
                    </select>
                    <input
                      placeholder="+7..."
                      value={phone.value}
                      onChange={(e) => handleUpdatePhone(index, e.target.value)}
                    />
                    <button onClick={() => handleDeletePhone(index)} className="delete-field-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="phones-list">
                {phones.length > 0 ? (
                  phones.map((phone, index) => (
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
                {emails.map((email, index) => (
                  <div key={index} className="email-edit-row">
                    <select
                      value={email.type}
                      onChange={(e) => {
                        const newEmails = emails.map((e, i) =>
                          i === index ? { ...e, type: e.target.value } : e
                        );
                        setEditData({ ...editData, emails: JSON.stringify(newEmails) });
                      }}
                    >
                      <option value="personal">Личный</option>
                      <option value="work">Рабочий</option>
                      <option value="other">Другой</option>
                    </select>
                    <input
                      type="email"
                      placeholder="email@example.com"
                      value={email.value}
                      onChange={(e) => handleUpdateEmail(index, e.target.value)}
                    />
                    <button onClick={() => handleDeleteEmail(index)} className="delete-field-btn">
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="emails-list">
                {emails.length > 0 ? (
                  emails.map((email, index) => (
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

          {/* Соцсети */}
          <div className="detail-section">
            <h3 className="section-title">
              <MessageCircle size={18} /> Соцсети
            </h3>
            {isEditing ? (
              <p className="no-data">Редактирование соцсетей в разработке</p>
            ) : (
              socials.length > 0 ? (
                <div className="socials-list">
                  {socials.map((social, index) => (
                    <div key={index} className="social-item">
                      <span className="social-type">{social.type}</span>
                      <a href={social.value} target="_blank" rel="noopener noreferrer">{social.value}</a>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">Нет соцсетей</p>
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

// Форма создания/редактирования контакта
function ContactForm({ isCreating, editData, setEditData, groups, onSave, onCancel }) {
  return (
    <div className="contact-detail-overlay">
      <div className="contact-detail">
        <div className="detail-header">
          <h2>{isCreating ? 'Новый контакт' : 'Редактирование контакта'}</h2>
          <div className="header-actions">
            <button onClick={onSave} className="icon-btn success" title="Сохранить">
              <Save size={20} />
            </button>
            <button onClick={onCancel} className="icon-btn" title="Отмена">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="detail-content">
          {/* Основная информация */}
          <div className="detail-section">
            <h3 className="section-title">Основная информация</h3>
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
                onChange={(e) => setEditData({ ...editData, group_id: e.target.value ? parseInt(e.target.value, 10) : null })}
              >
                <option value="">Без группы</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>{group.name}</option>
                ))}
              </select>
              <input
                type="date"
                placeholder="Дата рождения"
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
          </div>

          {/* Компания */}
          <div className="detail-section">
            <h3 className="section-title">
              <Building size={18} /> Место работы
            </h3>
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
          </div>

          {/* Адрес */}
          <div className="detail-section">
            <h3 className="section-title">
              <MapPin size={18} /> Адрес
            </h3>
            <textarea
              placeholder="Адрес"
              value={editData.address || ''}
              onChange={(e) => setEditData({ ...editData, address: e.target.value })}
              rows={2}
            />
          </div>

          {/* Сайт */}
          <div className="detail-section">
            <h3 className="section-title">
              <Globe size={18} /> Сайт
            </h3>
            <input
              placeholder="https://..."
              value={editData.website || ''}
              onChange={(e) => setEditData({ ...editData, website: e.target.value })}
            />
          </div>

          {/* Заметки */}
          <div className="detail-section">
            <h3 className="section-title">Заметки</h3>
            <textarea
              placeholder="Дополнительная информация"
              value={editData.notes || ''}
              onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
              rows={4}
            />
          </div>

          <div style={{ marginTop: '20px', color: '#668888', fontSize: '13px', fontStyle: 'italic' }}>
            Телефоны, Email и соцсети можно добавить после создания контакта
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContactPanel;
