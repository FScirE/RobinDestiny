import http.server
import webbrowser
import os
from dotenv import get_key
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta
import base64
from src.netreq import do_retry_request
from src.io import write_data_file, read_data_file

# This auth flow assumes it is only the local host that does the authorization.
# Multiple simultaneous oauth calls would not work.

OAUTH_FILE = "./oauth.json"
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

def check_refresh_token() -> bool:
    """
    Checks if refresh token exists or if outdated
    """
    if not os.path.isfile(OAUTH_FILE):
        return False
    data = read_data_file(OAUTH_FILE)
    expiry_date = datetime.fromisoformat(data["expiryDate"])
    if datetime.now(timezone.utc) > expiry_date:
        return False
    get_set_oauth() #valid refresh token can still fail on first attempt, this gets a new refresh token
    return True

def get_set_oauth(code: bool = None) -> str:
    """
    Gets OAuth access token given an authentication code, or using refresh token,
    and saves refresh token to file
    (psa: authentication code is one time use)
    """
    url = "https://www.bungie.net/platform/app/oauth/token/"
    id = get_key(".env", "CLIENT_ID")
    secret = get_key(".env", "CLIENT_SECRET")

    get = code is None

    coded = base64.b64encode(f"{id}:{secret}".encode()).decode("ascii")
    header = {
        "Authorization": "Basic " + coded,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    if get: #if no auth code provided use refresh token
        info = {
            "grant_type": "refresh_token",
            "refresh_token": read_data_file(OAUTH_FILE)["token"]
        }
    else:
        info = {
            "grant_type": "authorization_code",
            "code": code
        }
    data_raw = do_retry_request(False, False, url, header, data_http=info)
    if "error" in data_raw.json():
        return None
    data = data_raw.json()

    refresh_data = {
        "token": data["refresh_token"],
        "expiryDate": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    }
    write_data_file(refresh_data, OAUTH_FILE)
    return data["access_token"]
