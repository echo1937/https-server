import json
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = {"data": "hello"}
        self.wfile.write(bytes(json.dumps(message), 'utf-8'))


if __name__ == '__main__':
    # 创建 SSL/TLS 上下文
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # 加载证书和密钥
    context.load_cert_chain(certfile='/tmp/ca/example.crt', keyfile="/tmp/ca/example.key")

    # 创建 HTTP 服务器，并使用 wrap_socket() 方法包装 socket
    http_port = 4443
    httpd = HTTPServer(('localhost', http_port), MyRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    # 启动服务器
    print(f'Serving on port {http_port} (HTTPS) ...')
    httpd.serve_forever()
