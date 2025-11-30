#!/usr/bin/env python3
"""
Простое веб-приложение, которое возвращает "Hello World!".

Используем только стандартную библиотеку Python (http.server),
чтобы ничего не нужно было дополнительно устанавливать.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging


class HelloHandler(BaseHTTPRequestHandler):
    """HTTP-обработчик, который на любой GET-запрос возвращает 'Hello World!'."""

    def do_GET(self):
        logging.info("Получен запрос: %s", self.path)
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Hello World!".encode("utf-8"))

    # Переопределяем стандартный логгер, чтобы использовать logging-модуль
    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s",
                     self.client_address[0],
                     self.log_date_time_string(),
                     format % args)


def run(host: str = "0.0.0.0", port: int = 8000):
    """Запуск HTTP-сервера."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [APP] %(levelname)s: %(message)s"
    )
    server_address = (host, port)
    httpd = HTTPServer(server_address, HelloHandler)
    logging.info("Сервер запущен на %s:%s", host, port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Остановка сервера по Ctrl+C")
    finally:
        httpd.server_close()
        logging.info("Сервер остановлен")


if __name__ == "__main__":
    run()
