import http.server
import webbrowser
from dotenv import get_key
from urllib.parse import urlparse, parse_qs

# This auth flow assumes it is only the local host that does the authorization.
# Multiple simultaneous oauth calls would not work.

auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    """
    Request handler for the local http server that
    stores a received OAuth code and returns whether
    successful or not.
    """
    def do_GET(self):
        global auth_code

        url = urlparse(self.path)
        params = parse_qs(url.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200, "OAuth authentication successful")
            self.send_header("Content-type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
        else:
            auth_code = None
            self.send_error(400, "No OAuth authentication code was returned")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

def get_oauth_code() -> str:
    """
    Creates a local http server that handles one request
    with an OAuth code. Opens a browser window with bungie login,
    which redirects to a GitHub Pages site that sends a request
    to the local http server with the received code.
    """
    global auth_code
    auth_code = None

    server_address = ("127.0.0.1", 8000)
    httpd = http.server.HTTPServer(server_address, Handler)
    httpd.timeout = 60 # one minute timeout

    auth_url = get_key(".env", "AUTH_URL")
    webbrowser.open(auth_url)

    httpd.handle_request()
    httpd.server_close()

    return auth_code
