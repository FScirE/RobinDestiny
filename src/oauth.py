import http.server
import webbrowser
import ssl
from dotenv import get_key
from urllib.parse import urlparse, parse_qs
from src.ssl import generate_ssl_keys

auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code

        url = urlparse(self.path)
        params = parse_qs(url.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200, "OAuth authentication successful")
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<script>window.close();</script>")
        else:
            auth_code = None
            self.send_error(400, "No OAuth authentication code was returned")

# def get_oauth_code():
#     generate_ssl_keys()

#     server_address = ("127.0.0.1", 8000)
#     context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     context.load_cert_chain("ssl/cert.pem", "ssl/key.pem")

#     httpd = http.server.HTTPServer(server_address, Handler)
#     httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

#     auth_url = get_key(".env", "AUTH_URL")
#     webbrowser.open(auth_url)

#     httpd.handle_request()
#     httpd.server_close()

#     return auth_code