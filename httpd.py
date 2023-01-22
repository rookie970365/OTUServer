# pylint: disable=W0703
"""
 Многопоточный веб-сервер, частично реализующий протоĸол HTTP
"""
import argparse
import socket
import os
import mimetypes
from urllib.parse import unquote
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

PROTOCOL = 'HTTP/1.0'
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ALLOWED = 405
STATUSES = {
    OK: 'OK',
    BAD_REQUEST: 'Bad Request',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND: 'Not Found',
    NOT_ALLOWED: 'Method Not Allowed'
}
BUFFER_SIZE = 1024
TIMEOUT = 5
INDEX = 'index.html'


class HttpRequestHandler:
    """
    Класс обработчик http-запроса
    """
    def __init__(self, document_root):
        self.document_root = document_root
        self.method = 'GET'
        self.filepath = ''
        self.buffer = ''
        self.headers = {'Content-Type': 'text/html',
                        'Content-Length': '0',
                        'Server': 'OTUServer',
                        'Connection': 'close',
                        'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'), }

    def parse(self, request_str):
        """
        функция парсинга строки запроса
        """
        try:
            request = request_str.split('\r\n')
            method, query, _ = request[0].split()
            logging.info(request[0])
        except ValueError:
            return BAD_REQUEST

        if method not in ('GET', 'HEAD'):
            return NOT_ALLOWED
        self.method = method

        urlpath = unquote(query)
        if '?' in urlpath:
            urlpath, _ = urlpath.split('?')
        path = self.document_root + urlpath

        if not os.path.abspath(path).startswith(os.path.abspath(self.document_root)):
            return BAD_REQUEST
        if path.endswith('/') and os.path.isfile(os.path.join(self.document_root, path, INDEX)):
            self.filepath = os.path.join(self.document_root, path, INDEX)
        elif os.path.isfile(os.path.join(self.document_root, path)):
            self.filepath = os.path.join(self.document_root, path)
        return OK if self.filepath else NOT_FOUND

    def process_request(self, request_str):
        """
        функция обработки запроса
        """
        code = self.parse(request_str)
        response_lines = [f'{PROTOCOL} {code} {STATUSES[code]}']
        body = ''
        if code == OK:
            mtype, _ = mimetypes.guess_type(self.filepath)
            if mtype:
                self.headers['Content-Type'] = mtype
            filesize = os.path.getsize(self.filepath)
            self.headers['Content-Length'] = str(filesize)
            if self.method == 'GET':
                with open(self.filepath, 'rb') as f_p:
                    body = f_p.read(filesize)
        response_lines += [': '.join(item) for item in self.headers.items()]
        self.buffer = ('\r\n'.join(response_lines) + '\r\n\r\n').encode()
        if body:
            self.buffer += body
        return self.buffer


def handle_client(client_sock, document_root):
    """
    функция обработки подключения
    """
    buffer = b''
    while True:
        r_c = client_sock.recv(BUFFER_SIZE)
        if not r_c:
            raise socket.error('Server closed connection')
        buffer += r_c
        if b'\r\n\r\n' in buffer:
            break
    request_str = buffer.decode('utf8')
    handler = HttpRequestHandler(document_root)
    response = handler.process_request(request_str)
    client_sock.sendall(response)
    client_sock.shutdown(socket.SHUT_RDWR)


class MyHTTPServer:
    """
    класс многопоточный сервер
    """
    def __init__(self, host, port, qty_workers, document_root):
        self.host = host
        self.port = port
        self.qty_workers = qty_workers
        self.document_root = document_root

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def serve_forever(self):
        """
        функция запуска сервера
        :return:
        """
        self.server_sock.bind((self.host, self.port))
        logging.info("Listening at %s:%s", self.host, self.port)
        self.server_sock.listen()
        while True:
            try:
                client_sock, addr = self.server_sock.accept()
                logging.info("Connected by %s", repr(addr))
                client_sock.settimeout(TIMEOUT)
                with ThreadPoolExecutor(max_workers=self.qty_workers) as executor:
                    executor.submit(handle_client, client_sock, self.document_root)
            except Exception as ex:
                logging.info("Error during handling request. Details: %s", ex)

    def close(self):
        """
        функция выключения сервера
        """
        logging.info('server shutdown...')
        self.server_sock.shutdown(socket.SHUT_RDWR)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="HTTP server")
    parser.add_argument("-i", "--host", default="localhost", help="Host to listen")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to listen")
    parser.add_argument("-w", "--workers", type=int, default=5, help="Number of worker processes")
    parser.add_argument("-r", "--document_root", default=".", help="Document root")
    args = parser.parse_args()

    logging.basicConfig(filename=None, level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    server = MyHTTPServer(args.host, args.port, args.workers, args.document_root)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt. Stopping...")
    except Exception as exc:
        logging.exception("Unexpected error: %s", exc)
    finally:
        server.close()
        logging.info("Server stopped")
