# Как данные из базы попадают в Sidebar: подробное описание

## Общая архитектура

```
SQLite БД → Repository → API Endpoint → API Client (fetch) → React Hook → Component → UI
```

---

## 1. Уровень базы данных (`db/`)

### Файлы:
- **`db/database.py`** — подключение к SQLite, создание таблиц
- **`db/models.py`** — dataclass-модели (Note, Resource, Task, KategoryNote, etc.)
- **`db/repositories/*.py`** — CRUD-операции

### Ключевые репозитории:

| Репозиторий | Методы для sidebar |
|-------------|-------------------|
| `resource_repo.py` | `get_all()`, `get_categories()` |
| `note_repo.py` | `get_all()`, `get_categories()` |
| `task_repo.py` | `get_all()`, `get_categories()` |
| `folder_repo.py` | `get_all()`, `get_tree()` |

### Пример (resource_repo.py):

```python
def get_categories(self) -> List[KategoryResource]:
    cursor = self.conn.cursor()
    cursor.execute("SELECT id, name FROM kategory_resource ORDER BY name")
    return [KategoryResource.from_row(row) for row in cursor.fetchall()]
```

---

## 2. Уровень API (`server/`)

### Файлы:
- **`server/main.py`** — создание FastAPI app, подключение роутеров
- **`server/api/categories.py`** — эндпоинты для категорий
- **`server/api/resources.py`**, **`notes.py`**, **`tasks.py`**, **`folders_tags.py`**
- **`server/schemas.py`** — Pydantic-схемы для валидации

### Эндпоинты для sidebar:

```
GET /api/categories/resources  → категории ресурсов
GET /api/categories/notes      → категории заметок
GET /api/categories/tasks      → категории задач

GET /api/resources             → все ресурсы
GET /api/notes                 → все заметки
GET /api/tasks                 → все задачи

GET /api/folders               → папки
GET /api/tags                  → теги
```

### Пример (categories.py):

```python
@router.get("/resources", response_model=List[KategoryResourceResponse])
def get_resource_categories():
    conn = get_connection()
    repo = ResourceRepository(conn)
    return repo.get_categories()
```

---

## 3. Уровень API-клиента (`sidebar/src/api/client.js`)

### Структура:

```javascript
export const resourcesApi = {
  getAll: (kategoryId) => fetchApi(`/api/resources${params}`),
  getCategories: () => fetchApi('/api/categories/resources'),
  // ...
};

export const notesApi = { /* ... */ };
export const tasksApi = { /* ... */ };
export const foldersApi = { /* ... */ };
```

### Пример:

```javascript
getCategories: () => fetchApi('/api/categories/resources'),
```

Функция `fetchApi()` делает HTTP-запрос к бэкенду и возвращает JSON.

---

## 4. Уровень React-хуков (`sidebar/src/hooks/`)

### Ключевой хук: `useSidebarData.js`

### Контекст данных:

```javascript
const SidebarDataContext = createContext(null);

export function SidebarDataProvider({ children }) {
  const [resourcesData, setResourcesData] = useState({
    resources: [],
    categories: [],
    loading: true,
    error: null,
  });
  // ... аналогично для notes и tasks
```

### Загрузка данных при монтировании:

```javascript
useEffect(() => {
  loadResources();  // GET /api/resources + GET /api/categories/resources
  loadNotes();      // GET /api/notes + GET /api/categories/notes
  loadTasks();      // GET /api/tasks + GET /api/categories/tasks
}, [loadResources, loadNotes, loadTasks]);
```

### Пример функции загрузки:

```javascript
const loadResources = useCallback(async () => {
  try {
    setResourcesData(prev => ({ ...prev, loading: true }));
    const [resources, categories] = await Promise.all([
      resourcesApi.getAll(),
      resourcesApi.getCategories(),
    ]);
    setResourcesData(prev => ({ ...prev, resources, categories, loading: false }));
  } catch (err) {
    setResourcesData(prev => ({ ...prev, error: err.message, loading: false }));
  }
}, []);
```

---

## 5. Уровень компонентов (`sidebar/src/components/Sidebar.js`)

### Компоненты панелей:
- **`ResourcesPanel`** — отображает ресурсы по категориям
- **`NotesPanel`** — отображает заметки по категориям и папкам
- **`TasksPanel`** — отображает задачи по категориям

### Получение данных из контекста:

```javascript
function ResourcesPanel({ searchQuery, onItemSelect }) {
  const {
    resources,
    categories,
    loading,
    error,
    searchResources,
    createResource,
    deleteResource,
    // ...
  } = useSidebarData().resources;
```

### Отображение:

```javascript
{categories.map(category => {
  const categoryResources = resources.filter(item => item.kategory_id === category.id);
  return (
    <div key={category.id} className="tree-item">
      <div className="tree-node" onClick={() => toggleCategory(category.id)}>
        <span>{category.name}</span>
        <span className="count">{categoryResources.length}</span>
      </div>
      {expandedCategories.includes(category.id) && (
        <div className="tree-children">
          {categoryResources.map(item => (
            <div key={item.id} className="tree-leaf">
              <span>{item.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
})}
```

---

## 6. Обёртка приложения (`sidebar/src/App.js`)

```javascript
function App() {
  return (
    <SidebarDataProvider>  ← Провайдер контекста
      <AppContent />
    </SidebarDataProvider>
  );
}
```

---

## Полная цепочка для примера (категории ресурсов)

| Шаг | Компонент | Код |
|-----|-----------|-----|
| 1 | SQLite таблица | `kategory_resource(id, name)` |
| 2 | Репозиторий | `ResourceRepository.get_categories()` → SQL SELECT |
| 3 | API эндпоинт | `GET /api/categories/resources` → `repo.get_categories()` |
| 4 | API клиент | `resourcesApi.getCategories()` → `fetch('/api/categories/resources')` |
| 5 | Хук | `loadResources()` в `useSidebarData.js` → вызов API |
| 6 | Контекст | `setResourcesData({ categories: [...] })` |
| 7 | Компонент | `useSidebarData().resources.categories` |
| 8 | UI | Рендеринг дерева категорий в `ResourcesPanel` |

---

## Точки, где могут возникнуть проблемы

1. **БД**: таблица пуста / нет данных
2. **Репозиторий**: ошибка в SQL-запросе
3. **API**: эндпоинт не подключён в `main.py`
4. **API клиент**: неверный URL (`REACT_APP_API_URL`)
5. **Хук**: ошибка в `useEffect` / не вызывается `loadResources()`
6. **Компонент**: данные не передаются в компонент / ошибка в фильтре
7. **CORS**: бэкенд не разрешает запросы с фронтенда
