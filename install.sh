#!/usr/bin/env bash
# Скрипт автоматической установки/обновления решения.
# Выполнять: sudo ./install.sh

set -e

APP_DIR="/opt/hello_monitoring"
SYSTEMD_DIR="/etc/systemd/system"

echo "[*] Копируем файлы в ${APP_DIR} ..."
mkdir -p "${APP_DIR}"
cp app.py monitor.py config.ini "${APP_DIR}"

echo "[*] Копируем unit-файлы systemd ..."
cp helloapp.service helloapp-monitor.service helloapp-monitor.timer "${SYSTEMD_DIR}"

echo "[*] Перечитываем конфигурацию systemd ..."
systemctl daemon-reload

echo "[*] Включаем автозапуск сервиса приложения и таймера мониторинга ..."
systemctl enable helloapp.service
systemctl enable helloapp-monitor.timer

echo "[*] Запускаем приложение и таймер мониторинга ..."
systemctl restart helloapp.service
systemctl restart helloapp-monitor.timer

echo "[*] Готово."
echo "  Проверить статус приложения:  sudo systemctl status helloapp.service"
echo "  Проверить статус мониторинга: sudo systemctl status helloapp-monitor.service"
echo "  Проверить таймер:             sudo systemctl list-timers | grep helloapp"
