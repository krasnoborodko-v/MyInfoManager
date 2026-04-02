# Быстрый старт MyInfoManager

## Запуск (2 шага)

### 1. Сервер (терминал 1)
```bash
cd v:\work\MyInfoManager
uvicorn server.main:app --reload
```
✅ Проверка: http://localhost:8000/health

### 2. Фронтенд (терминал 2)
```bash
cd v:\work\MyInfoManager\sidebar
npm start
```
✅ Проверка: http://localhost:3000

---

## Документация

| Файл | Описание |
|------|----------|
| [docs/SUMMARY.md](docs/SUMMARY.md) | 📚 Полная сводка проекта |
| [docs/api.md](docs/api.md) | 🔌 API эндпоинты |
| [docs/database.md](docs/database.md) | 💾 Структура БД |
| [docs/features.md](docs/features.md) | ⚙️ Список функций |
| [.qwen/context.md](.qwen/context.md) | 📝 Контекст разработки |

---

## Тесты

```bash
pytest tests/ -v
```

---

## Структура

```
MyInfoManager/
├── sidebar/       # React (порт 3000)
├── server/        # FastAPI (порт 8000)
├── db/            # База данных
├── docs/          # Документация
└── data/          # Файл БД (myinfo.db)
```

---

**Статус:** ✅ Готов к использованию
