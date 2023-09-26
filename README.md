# https-server

快速架设Python HTTPS服务


### 0. 前言
内网有一些接口是https的，由于开发调试需要，需要自建https环境供测试使用。
### 1. 使用 OpenSSL 生成密钥和证书文件
```shell
mkdir -p /tmp/ca && cd /tmp/ca
openssl req -newkey rsa:2048 -nodes -keyout example.key -x509 -days 365 -out example.crt
```
这是一个使用 OpenSSL 工具生成自签名证书的命令。它会要求你输入一些相关信息，例如Country Name、State of Province Name、Locality Name等。你可以根据自己的实际情况进行填写。

执行完上述命令后，当前目录下就会生成 example.key 和 example.crt 文件。example.key 是私钥文件，而 example.crt 是自签名证书文件。

以下是各个选项的解释：
- `req` 是 OpenSSL 工具的一个子命令，用于处理证书签名请求。
- `-newkey rsa:2048` 选项表示要创建一个新的 RSA 密钥，并将其长度设置为 2048 位。这个密钥将用于后续的证书请求和签名操作。
- `-nodes` 选项表示不要对私钥进行加密，即使私钥被泄露也不会对其进行保护。这在测试和开发过程中很有用，但在生产环境中不建议使用。
- `-keyout example.key` 选项指定了生成的私钥文件的路径和名称。
- `-x509` 选项表示生成一个自签名的 X.509 格式证书，而不是一个证书请求。
- `-days 365` 选项表示证书的有效期为一年，可以根据需要进行更改。
- `-out example.crt` 选项指定了生成的证书文件的路径和名称。

> 以上信息由ChatGPT生成的。

### 2. 启动Python 3的HTTPS服务器
青春版
```python
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
```
双模版
```python
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

```
IPv6双模版
```python
import json
import socket
import ssl
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


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
    HTTPServerV6((http_host, http_port), MyRequestHandler).serve_forever()


def start_https_server(http_host, http_port):
    # 创建 SSL/TLS 上下文
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # 加载证书和密钥
    context.load_cert_chain(certfile='/tmp/ca/example.crt', keyfile="/tmp/ca/example.key")

    # 创建 HTTP 服务器，并使用 wrap_socket() 方法包装 socket
    httpd = HTTPServerV6((http_host, http_port), MyRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    # 启动服务器
    print(f'Serving on port {http_port} (HTTPS) ...')
    httpd.serve_forever()


if __name__ == '__main__':
    # 启动HTTP服务
    http_thread = threading.Thread(target=start_http_server, args=('::', 8000))
    http_thread.start()

    # 启动HTTPS服务
    https_thread = threading.Thread(target=start_https_server, args=('::', 8443))
    https_thread.start()
```

### 3. 扩展链接
- [简单的 Python HTTP(S) 服务器](https://bbs.huaweicloud.com/blogs/313283)
- [为Python HTTP(s)服务器添加IPv6支持](https://gist.github.com/akorobov/7903307)