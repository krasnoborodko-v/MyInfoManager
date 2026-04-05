# Справочник команд администратора сервера

## Подключение к серверу (с Windows)

```powershell
# Базовое подключение
ssh valery@192.168.1.110

# Если ошибка ключа — очистить старый:
ssh-keygen -R 192.168.1.110
ssh valery@192.168.1.110
```

---
СТАРТ после загрузки

```bash
cd ~/MyInfoManager
./start-server.sh
```

---

## Файловая система

```bash
ls              # Список файлов
ls -la          # Список с правами и скрытыми файлами
cd ~/MyInfoManager  # Перейти в папку проекта
pwd             # Показать текущую директорию
cp файл1 файл2  # Копировать
mv файл1 файл2  # Переименовать/переместить
rm файл         # Удалить файл
rm -rf папка    # Удалить папку
mkdir папка     # Создать папку
nano файл       # Редактировать файл
```

### Редактор nano

| Комбинация | Действие |
|------------|----------|
| `Ctrl+O` | Сохранить |
| `Enter` | Подтвердить имя файла |
| `Ctrl+X` | Выход |
| `Ctrl+K` | Вырезать строку |
| `Ctrl+U` | Вставить строку |

---

## Системная информация

```bash
uname -a          # Версия ядра
free -h           # Память RAM
df -h             # Место на дисках
lsblk             # Диски и разделы
top               # Процессы (q — выход)
htop              # Процессы красивее (q — выход)
cat /etc/os-release  # Версия Ubuntu
uptime            # Время работы
```

---

## Сеть

```bash
ip addr show              # IP-адреса
ip route                  # Маршруты
ss -tlnp                  # Прослушиваемые порты
curl http://localhost:8000/health  # Проверка API
ping ya.ru                # Проверка интернета
```

---

## Docker — основной инструмент

### Управление контейнерами

```bash
docker compose ps          # Статус контейнеров
docker compose up -d       # Запустить все
docker compose up -d --build  # Пересобрать и запустить
docker compose down        # Остановить
docker compose down -v     # Остановить + удалить тома (данные!)
docker compose restart     # Перезапустить
```

### Логи

```bash
docker compose logs                  # Все логи
docker compose logs -f               # Логи в реальном времени
docker compose logs myinfomanager    # Логи одного сервиса
docker compose logs --tail 50        # Последние 50 строк
```

### Управление образами

```bash
docker images            # Список образов
docker rmi имя_образа    # Удалить образ
docker system prune      # Очистить неиспользуемое
```

### Внутри контейнера

```bash
docker exec -it имя_контейнера sh      # Войти в контейнер
docker exec myinfomanager-db psql -U myinfo -d myinfomanager  # Войти в БД
docker stats                           # Ресурсы контейнеров
```

---

## Git

```bash
git pull                    # Обновить код
git status                  # Состояние репозитория
git log --oneline -5        # Последние 5 коммитов
git diff                    # Изменения в файлах
```

---

## Перезапуск MyInfoManager после изменений

```bash
cd ~/MyInfoManager

# Если код изменился (git pull или правка файлов):
git pull
docker compose up -d --build

# Если изменился только конфиг infra/:
cd ~/MyInfoManager/infra
docker compose up -d --build
```

---

## Сервисы systemd

```bash
sudo systemctl status ssh          # Статус SSH
sudo systemctl restart ssh         # Перезапуск SSH
sudo systemctl enable ssh          # Автозапуск при загрузке
sudo systemctl status docker       # Статус Docker
sudo systemctl restart docker      # Перезапуск Docker
```

---

## Бэкап базы данных

```bash
# Сделать дамп
docker exec myinfomanager-db pg_dump -U myinfo -d myinfomanager > ~/backup_$(date +%Y%m%d).sql

# Восстановить из дампа
docker exec -i myinfomanager-db psql -U myinfo -d myinfomanager < ~/backup_20260404.sql
```

---

## Полезные мелочи

```bash
history              # История команд
!!                   # Повторить последнюю команду
sudo !!              # Повторить с правами root
clear                # Очистить экран
exit                 # Выйти из SSH
```

---

## Адреса и порты

| Что | Адрес |
|-----|-------|
| SSH | `ssh valery@192.168.1.110` |
| MyInfoManager HTTP | `http://192.168.1.110:8000` |
| MyInfoManager HTTPS (после настройки) | `https://myinfo.local` |
| Nginx (после настройки) | `http://192.168.1.110:80` / `https://192.168.1.110:443` |

---

## Типичный рабочий цикл

```bash
# 1. Подключились
ssh valery@192.168.1.110

# 2. Зашли в проект
cd ~/MyInfoManager

# 3. Обновили код (если правили на Windows и пушили)
git pull

# 4. Пересобрали и перезапустили
docker compose down
docker compose up -d --build

# 5. Проверили
curl http://localhost:8000/health
docker compose ps
docker compose logs myinfomanager --tail 20
```
