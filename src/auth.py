import webbrowser
import urllib.parse
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests
import base64
import json

load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = "http://127.0.0.1:8888/callback/"
scopes = "playlist-modify-private playlist-modify-public"



def get_auth_code():
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes
    })
    class CallbackHandler(BaseHTTPRequestHandler):
        auth_code = None
        def do_GET(self):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                CallbackHandler.auth_code = params["code"][0]
                #print("Authorization code:", CallbackHandler.auth_code)
                self.send_response(200)
                #self.end_headers()
                self.wfile.write(b"You can close this window now.")
            else:
                self.send_response(400)
                self.end_headers()

    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    print("Waiting for Spotify redirect...")
    webbrowser.open(auth_url)
    print("Go to the URL above and log in.")
    try:
        server.handle_request()
    except Exception as e:
        print("Error while waiting for redirect:", e)
    finally:
        server.server_close()

    if CallbackHandler.auth_code is None:
        print("Authorization failed or was canceled.")

    return CallbackHandler.auth_code

def get_tokens(auth_code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
    }

    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()

def refresh_access_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()['access_token']