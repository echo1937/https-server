import json
import ssl
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class MyRequestHandler(BaseHTTPRequestHandler):
    message = {"data": "hello"}

    def send_json_response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(content.encode(encoding='utf-8'))

    def do_GET(self):
        print("Headers: ", self.headers)
        self.send_json_response(json.dumps(self.message))


def start_http_server(http_host, http_port):
    print(f'Serving on port {http_port} (HTTP) ...')
    HTTPServer((http_host, http_port), MyRequestHandler).serve_forever()


def start_https_server(http_host, http_port):
    # 创建 SSL/TLS 上下文
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # 加载证书和密钥
    context.load_cert_chain(certfile='/tmp/ca/example.crt', keyfile="/tmp/ca/example.key")

    # 创建 HTTP 服务器，并使用 wrap_socket() 方法包装 socket
    httpd = HTTPServer((http_host, http_port), MyRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    # 启动服务器
    print(f'Serving on port {http_port} (HTTPS) ...')
    httpd.serve_forever()


if __name__ == '__main__':
    # 启动HTTP服务
    http_thread = threading.Thread(target=start_http_server, args=('localhost', 8000))
    http_thread.start()

    # 启动HTTPS服务
    https_thread = threading.Thread(target=start_https_server, args=('localhost', 8443))
    https_thread.start()

