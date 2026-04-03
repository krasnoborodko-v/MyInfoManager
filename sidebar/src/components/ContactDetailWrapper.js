import React, { useState } from 'react';
import {
  X, Edit2, Trash2, Save, Plus,
  Phone, Mail, MessageCircle, Building, MapPin, Globe,
  Upload, Image, Calendar, Star, Heart
} from 'lucide-react';
import { useContacts } from '../hooks';

/**
 * Полнофункциональная форма деталей контакта.
 */
export function ContactDetailWrapper({ id, onClose }) {
  const { groups, updateContact, deleteContact, uploadPhoto, deletePhoto, getContactById } = useContacts();
  const [contact, setContact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(null);

  React.useEffect(() => {
    const loadContact = async () => {
      setLoading(true);
      try {
        const loaded = await getContactById(id);
        setContact(loaded);
      } catch (err) {
        console.error('Failed to load contact:', err);
      } finally {
        setLoading(false);
      }
    };
    loadContact();
  }, [id, getContactById]);

  React.useEffect(() => {
    if (contact) {
      setEditData({
        ...contact,
        birth_date: contact.birth_date ? contact.birth_date.slice(0, 10) : ''
      });
    }
  }, [contact]);

  // При загрузке фото обновляем editData
  React.useEffect(() => {
    if (contact?.photo && editData) {
      setEditData(prev => ({
        ...prev,
        photo: contact.photo,
        photo_type: contact.photo_type
      }));
    }
  }, [contact?.photo, contact?.photo_type]);

  const handleSave = async () => {
    // Не отправляем фото на сервер - оно уже сохранено
    const { photo, photo_type, ...dataWithoutPhoto } = editData;
    await updateContact(contact.id, dataWithoutPhoto);
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
      const updated = await getContactById(contact.id);
      setContact(updated);
      // Сразу обновляем editData с фото
      setEditData(prev => ({
        ...prev,
        photo: updated?.photo || null,
        photo_type: updated?.photo_type || null
      }));
    }
  };

  const handleDeletePhoto = async () => {
    await deletePhoto(contact.id);
    const updated = await getContactById(contact.id);
    setContact(updated);
    // Обновляем editData без фото
    setEditData(prev => ({
      ...prev,
      photo: null,
      photo_type: null
    }));
  };

  const parseJson = (str) => {
    try { return str ? JSON.parse(str) : []; } catch { return []; }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  // Телефоны
  const handleAddPhone = () => {
    const phones = parseJson(editData.phones);
    setEditData({ ...editData, phones: JSON.stringify([...phones, { type: 'mobile', value: '' }]) });
  };
  const handleUpdatePhone = (index, field, value) => {
    const phones = parseJson(editData.phones);
    phones[index] = { ...phones[index], [field]: value };
    setEditData({ ...editData, phones: JSON.stringify(phones) });
  };
  const handleDeletePhone = (index) => {
    const phones = parseJson(editData.phones).filter((_, i) => i !== index);
    setEditData({ ...editData, phones: JSON.stringify(phones) });
  };

  // Email
  const handleAddEmail = () => {
    const emails = parseJson(editData.emails);
    setEditData({ ...editData, emails: JSON.stringify([...emails, { type: 'personal', value: '' }]) });
  };
  const handleUpdateEmail = (index, field, value) => {
    const emails = parseJson(editData.emails);
    emails[index] = { ...emails[index], [field]: value };
    setEditData({ ...editData, emails: JSON.stringify(emails) });
  };
  const handleDeleteEmail = (index) => {
    const emails = parseJson(editData.emails).filter((_, i) => i !== index);
    setEditData({ ...editData, emails: JSON.stringify(emails) });
  };

  // Соцсети
  const handleAddSocial = () => {
    const socials = parseJson(editData.socials);
    setEditData({ ...editData, socials: JSON.stringify([...socials, { type: 'telegram', value: '' }]) });
  };
  const handleUpdateSocial = (index, field, value) => {
    const socials = parseJson(editData.socials);
    socials[index] = { ...socials[index], [field]: value };
    setEditData({ ...editData, socials: JSON.stringify(socials) });
  };
  const handleDeleteSocial = (index) => {
    const socials = parseJson(editData.socials).filter((_, i) => i !== index);
    setEditData({ ...editData, socials: JSON.stringify(socials) });
  };

  if (loading) return <div className="not-found">Загрузка...</div>;
  if (!contact) return <div className="not-found">Контакт не найден</div>;

  return (
    <div className="contact-detail-overlay">
      <div className="contact-detail">
        <div className="detail-header">
          <h2>{contact.last_name} {contact.first_name} {contact.middle_name}</h2>
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
                <input placeholder="Фамилия" value={editData.last_name} onChange={(e) => setEditData({ ...editData, last_name: e.target.value })} />
                <input placeholder="Имя" value={editData.first_name} onChange={(e) => setEditData({ ...editData, first_name: e.target.value })} />
                <input placeholder="Отчество" value={editData.middle_name || ''} onChange={(e) => setEditData({ ...editData, middle_name: e.target.value })} />
                <select value={editData.group_id || ''} onChange={(e) => setEditData({ ...editData, group_id: e.target.value ? parseInt(e.target.value) : null })}>
                  <option value="">Без группы</option>
                  {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                </select>
                <input type="date" value={editData.birth_date || ''} onChange={(e) => setEditData({ ...editData, birth_date: e.target.value })} />
                <label className="checkbox-label">
                  <input type="checkbox" checked={editData.is_favorite} onChange={(e) => setEditData({ ...editData, is_favorite: e.target.checked })} />
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
                    <span className="info-value"><Calendar size={14} /> {formatDate(contact.birth_date)}</span>
                  </div>
                )}
                {contact.is_favorite && (
                  <div className="info-item">
                    <span className="info-label"><Star size={14} fill="currentColor" /> Избранный</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Телефоны */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title"><Phone size={18} /> Телефоны</h3>
              {isEditing && <button onClick={handleAddPhone} className="add-btn"><Plus size={16} /></button>}
            </div>
            {isEditing ? (
              <div className="phones-edit">
                {parseJson(editData.phones).map((phone, index) => (
                  <div key={index} className="phone-edit-row">
                    <select value={phone.type} onChange={(e) => handleUpdatePhone(index, 'type', e.target.value)}>
                      <option value="mobile">Мобильный</option>
                      <option value="work">Рабочий</option>
                      <option value="home">Домашний</option>
                      <option value="other">Другой</option>
                    </select>
                    <input placeholder="+7..." value={phone.value} onChange={(e) => handleUpdatePhone(index, 'value', e.target.value)} />
                    <button onClick={() => handleDeletePhone(index)} className="delete-field-btn"><X size={14} /></button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="phones-list">
                {parseJson(contact.phones).length > 0 ? parseJson(contact.phones).map((phone, i) => (
                  <div key={i} className="phone-item">
                    <span className="phone-type">{phone.type === 'mobile' ? 'Моб.' : phone.type === 'work' ? 'Рабочий' : phone.type === 'home' ? 'Дом.' : 'Др.'}</span>
                    <a href={`tel:${phone.value}`}>{phone.value}</a>
                  </div>
                )) : <p className="no-data">Нет телефонов</p>}
              </div>
            )}
          </div>

          {/* Email */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title"><Mail size={18} /> Email</h3>
              {isEditing && <button onClick={handleAddEmail} className="add-btn"><Plus size={16} /></button>}
            </div>
            {isEditing ? (
              <div className="emails-edit">
                {parseJson(editData.emails).map((email, index) => (
                  <div key={index} className="email-edit-row">
                    <select value={email.type} onChange={(e) => handleUpdateEmail(index, 'type', e.target.value)}>
                      <option value="personal">Личный</option>
                      <option value="work">Рабочий</option>
                      <option value="other">Другой</option>
                    </select>
                    <input type="email" placeholder="email@example.com" value={email.value} onChange={(e) => handleUpdateEmail(index, 'value', e.target.value)} />
                    <button onClick={() => handleDeleteEmail(index)} className="delete-field-btn"><X size={14} /></button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="emails-list">
                {parseJson(contact.emails).length > 0 ? parseJson(contact.emails).map((email, i) => (
                  <div key={i} className="email-item">
                    <span className="email-type">{email.type === 'personal' ? 'Личный' : email.type === 'work' ? 'Рабочий' : 'Др.'}</span>
                    <a href={`mailto:${email.value}`}>{email.value}</a>
                  </div>
                )) : <p className="no-data">Нет email</p>}
              </div>
            )}
          </div>

          {/* Соцсети */}
          <div className="detail-section">
            <div className="section-title-row">
              <h3 className="section-title"><MessageCircle size={18} /> Соцсети</h3>
              {isEditing && <button onClick={handleAddSocial} className="add-btn"><Plus size={16} /></button>}
            </div>
            {isEditing ? (
              <div className="socials-edit">
                {parseJson(editData.socials).map((social, index) => (
                  <div key={index} className="social-edit-row">
                    <select value={social.type} onChange={(e) => handleUpdateSocial(index, 'type', e.target.value)}>
                      <option value="telegram">Telegram</option>
                      <option value="whatsapp">WhatsApp</option>
                      <option value="viber">Viber</option>
                      <option value="vk">VK</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                      <option value="other">Другой</option>
                    </select>
                    <input placeholder="@username или ссылка" value={social.value} onChange={(e) => handleUpdateSocial(index, 'value', e.target.value)} />
                    <button onClick={() => handleDeleteSocial(index)} className="delete-field-btn"><X size={14} /></button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="socials-list">
                {parseJson(contact.socials).length > 0 ? parseJson(contact.socials).map((social, i) => (
                  <div key={i} className="social-item">
                    <span className="social-type">{social.type}</span>
                    <a href={social.value.startsWith('http') ? social.value : `https://${social.type}.com/${social.value}`} target="_blank" rel="noopener noreferrer">{social.value}</a>
                  </div>
                )) : <p className="no-data">Нет соцсетей</p>}
              </div>
            )}
          </div>

          {/* Работа */}
          <div className="detail-section">
            <h3 className="section-title"><Building size={18} /> Место работы</h3>
            {isEditing ? (
              <div className="edit-row">
                <input placeholder="Организация" value={editData.company || ''} onChange={(e) => setEditData({ ...editData, company: e.target.value })} />
                <input placeholder="Должность" value={editData.position || ''} onChange={(e) => setEditData({ ...editData, position: e.target.value })} />
              </div>
            ) : (
              <div className="info-grid">
                {contact.company ? <div className="info-item"><span className="info-label">Организация:</span><span className="info-value">{contact.company}</span></div> : <p className="no-data">Не указано</p>}
                {contact.position && <div className="info-item"><span className="info-label">Должность:</span><span className="info-value">{contact.position}</span></div>}
              </div>
            )}
          </div>

          {/* Адрес */}
          <div className="detail-section">
            <h3 className="section-title"><MapPin size={18} /> Адрес</h3>
            {isEditing ? (
              <textarea placeholder="Адрес" value={editData.address || ''} onChange={(e) => setEditData({ ...editData, address: e.target.value })} rows={2} />
            ) : (
              contact.address ? <p className="info-value">{contact.address}</p> : <p className="no-data">Не указан</p>
            )}
          </div>

          {/* Сайт */}
          <div className="detail-section">
            <h3 className="section-title"><Globe size={18} /> Сайт</h3>
            {isEditing ? (
              <input placeholder="https://..." value={editData.website || ''} onChange={(e) => setEditData({ ...editData, website: e.target.value })} />
            ) : (
              contact.website ? <a href={contact.website} target="_blank" rel="noopener noreferrer" className="info-value">{contact.website}</a> : <p className="no-data">Не указан</p>
            )}
          </div>

          {/* Заметки */}
          <div className="detail-section">
            <h3 className="section-title">Заметки</h3>
            {isEditing ? (
              <textarea placeholder="Дополнительная информация" value={editData.notes || ''} onChange={(e) => setEditData({ ...editData, notes: e.target.value })} rows={4} />
            ) : (
              contact.notes ? <p className="notes-content">{contact.notes}</p> : <p className="no-data">Нет заметок</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
