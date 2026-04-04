import React, { useState, useEffect } from 'react';
import { getAuthToken, authApi, refreshAccessToken } from './api/client';
import LoginPage from './components/LoginPage';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('resources');
  const [selectedItemId, setSelectedItemId] = useState(null);

  // При загрузке — проверяем токен
  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (!token) {
        setAuthLoading(false);
        return;
      }

      // Пробуем refresh если токен просрочен
      try {
        const userData = await authApi.me();
        setUser(userData);
      } catch {
        // Пробуем refresh
        const newToken = await refreshAccessToken();
        if (newToken) {
          try {
            const userData = await authApi.me();
            setUser(userData);
          } catch {
            setUser(null);
          }
        } else {
          setUser(null);
        }
      } finally {
        setAuthLoading(false);
      }
    };

    initAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
  };

  const handleItemSelect = (itemId) => {
    setSelectedItemId(itemId);
  };

  const handleSectionChange = (sectionId) => {
    setActiveSection(sectionId);
    setSelectedItemId(null);
  };

  useEffect(() => {
    setSelectedItemId(null);
  }, [activeSection]);

  // Загрузка
  if (authLoading) {
    return <div className="app-loading">Загрузка...</div>;
  }

  // Не авторизован — показываем страницу входа
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // Авторизован — основное приложение
  const hideSidebar = activeSection === 'contacts';

  return (
    <div className="app">
      {!hideSidebar && (
        <Sidebar
          activeSection={activeSection}
          onSectionChange={handleSectionChange}
          onItemSelect={handleItemSelect}
          user={user}
          onLogout={handleLogout}
        />
      )}
      <MainPanel
        activeSection={activeSection}
        selectedItemId={selectedItemId}
        onItemSelect={handleItemSelect}
        user={user}
      />
    </div>
  );
}

export default App;
