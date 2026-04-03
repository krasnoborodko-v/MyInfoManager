"""
Лаунчер MyInfoManager — единая точка входа для EXE.
Запускает uvicorn, открывает браузер, корректно завершает работу.
"""
import os
import sys
import webbrowser
import threading
import time


def get_base_dir():
    """Получить базовую директорию (для PyInstaller onefile — _MEIPASS)."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def open_browser():
    """Открыть браузер через 2 секунды после запуска сервера."""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8000')


def main():
    print("=" * 50)
    print("   MyInfoManager")
    print("=" * 50)
    print()

    # Определяем порт
    port = int(os.environ.get("PORT", 8000))

    # Открываем браузер в отдельном потоке
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Импортируем и запускаем uvicorn
    import uvicorn
    from server.main import app

    print(f"[+] Запуск сервера на http://127.0.0.1:{port}")
    print("[+] Приложение откроется в браузере автоматически")
    print("[+] Нажмите Ctrl+C для остановки")
    print()

    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
    except KeyboardInterrupt:
        print("\n[*] Остановка сервера...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    print("[*] Сервер остановлен")


if __name__ == "__main__":
    main()
