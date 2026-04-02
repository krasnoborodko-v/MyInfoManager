import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import './App.css';

function App() {
  const [activeSection, setActiveSection] = useState('resources');
  const [selectedItemId, setSelectedItemId] = useState(null);

  const handleItemSelect = (itemId) => {
    setSelectedItemId(itemId);
  };

  const handleSectionChange = (sectionId) => {
    setActiveSection(sectionId);
    // Сбрасываем выбранный элемент при смене раздела
    setSelectedItemId(null);
  };

  // Сбрасываем selectedItemId при изменении activeSection
  useEffect(() => {
    setSelectedItemId(null);
  }, [activeSection]);

  return (
    <div className="app">
      <Sidebar
        activeSection={activeSection}
        onSectionChange={handleSectionChange}
        onItemSelect={handleItemSelect}
      />
      <MainPanel
        activeSection={activeSection}
        selectedItemId={selectedItemId}
        onItemSelect={handleItemSelect}
      />
    </div>
  );
}

export default App;
