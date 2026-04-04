-- ============================================================
-- Инициализация PostgreSQL — создание БД и пользователей
-- для сервисов платформы
-- ============================================================

-- MyInfoManager
CREATE USER myinfo WITH PASSWORD 'myinfo_secret';
CREATE DATABASE myinfomanager OWNER myinfo;
GRANT ALL PRIVILEGES ON DATABASE myinfomanager TO myinfo;

-- Будущие сервисы (шаблон):
-- CREATE USER blog WITH PASSWORD 'blog_secret';
-- CREATE DATABASE blog OWNER blog;
-- GRANT ALL PRIVILEGES ON DATABASE blog TO blog;
