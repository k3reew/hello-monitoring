#!/usr/bin/env python3
"""
Скрипт мониторинга веб-приложения.

Функционал:
- проверка доступности HTTP-URL;
- логирование результатов проверки;
- перезапуск приложения через systemd в случае недоступности.
"""

import configparser
import logging
import os
import subprocess
import sys
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


def load_config(config_path: str = "config.ini"):
    """Загрузка параметров из конфигурационного файла."""
    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise FileNotFoundError(f"Не удалось прочитать {config_path}")
    return config


def setup_logging(log_file: str):
    """Настройка логирования в файл и stdout."""
    handlers = [logging.StreamHandler(sys.stdout)]
    # Логируем и в файл, если он указан
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [MONITOR] %(levelname)s: %(message)s",
        handlers=handlers,
    )


def check_app(url: str) -> bool:
    """Проверка доступности приложения по HTTP-URL."""
    try:
        with urlopen(url, timeout=5) as response:
            status = response.getcode()
            if status == 200:
                logging.info("Приложение доступно (HTTP %s)", status)
                return True
            else:
                logging.error("Приложение вернуло неожиданный код HTTP %s", status)
                return False
    except HTTPError as e:
        logging.error("HTTP ошибка при обращении к приложению: %s", e)
        return False
    except URLError as e:
        logging.error("Ошибка сети/доступа к приложению: %s", e)
        return False
    except Exception as e:
        logging.exception("Неожиданная ошибка при проверке приложения: %s", e)
        return False


def restart_app(service_name: str):
    """Перезапуск приложения через systemd."""
    # Добавим расширение .service, если его нет
    if not service_name.endswith(".service"):
        service_name = service_name + ".service"

    logging.info("Пытаемся перезапустить сервис %s", service_name)
    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logging.info("Сервис %s успешно перезапущен", service_name)
        else:
            logging.error(
                "Не удалось перезапустить сервис %s. Код=%s, stdout=%s, stderr=%s",
                service_name,
                result.returncode,
                result.stdout,
                result.stderr,
            )
    except Exception as e:
        logging.exception("Ошибка при попытке перезапуска сервиса: %s", e)


def main():
    """Точка входа: одна проверка и при необходимости перезапуск."""
    # Конфиг ожидаем в текущем рабочем каталоге (см. WorkingDirectory в unit-файле)
    config_path = os.environ.get("HELLO_MONITOR_CONFIG", "config.ini")

    config = load_config(config_path)
    app_url = config["app"]["url"].strip()
    service_name = config["app"]["service_name"].strip()
    log_file = config["monitor"].get("log_file", "monitor.log").strip()

    setup_logging(log_file)
    logging.info("Запуск мониторинга. URL=%s, сервис=%s", app_url, service_name)

    if not check_app(app_url):
        logging.warning("Приложение недоступно. Запускаем перезапуск сервиса.")
        restart_app(service_name)
    else:
        logging.info("Перезапуск не требуется.")


if __name__ == "__main__":
    main()
