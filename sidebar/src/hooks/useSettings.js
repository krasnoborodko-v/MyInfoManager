import { useState, useEffect, useCallback } from 'react';
import { settingsApi } from '../api/client';

/**
 * Хук для работы с настройками.
 * @returns {Object} - Состояние и методы для работы с настройками
 */
export function useSettings() {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Загрузка всех настроек
  const loadSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsApi.getAll();
      // Преобразуем в удобный формат
      const settingsObj = {};
      Object.keys(data).forEach(key => {
        settingsObj[key] = data[key].value;
      });
      setSettings(settingsObj);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Обновление настройки
  const updateSetting = useCallback(async (key, value) => {
    try {
      await settingsApi.update(key, value);
      setSettings(prev => ({ ...prev, [key]: value }));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  }, []);

  // Получение конкретной настройки
  const getSetting = useCallback((key, defaultValue) => {
    return settings[key] !== undefined ? settings[key] : defaultValue;
  }, [settings]);

  // Загрузка при монтировании
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  return {
    settings,
    loading,
    error,
    loadSettings,
    updateSetting,
    getSetting,
  };
}

export default useSettings;
