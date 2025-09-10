from src import refresh_access_token,get_auth_code,get_tokens,write_refresh_token_to_env
from dotenv import load_dotenv
import os
load_dotenv()

def main_auth():
    refresh_token = os.getenv("refresh_token")
    access_token = None
    if refresh_token:
        access_token = refresh_access_token(refresh_token)
        print("Access token refreshed:", access_token)
    else:
        print("No refresh token found. Starting authentication flow...")
        auth_code = get_auth_code()
        if auth_code:
            tokens = get_tokens(auth_code)
            print("Access token:", tokens.get("access_token"))
            print("Refresh token:", tokens.get("refresh_token"))
            access_token = tokens.get("access_token")
            refresh_token= tokens.get("refresh_token")
            if refresh_token:
                write_refresh_token_to_env(refresh_token)

        else:
            print("Authentication failed.")
    return(access_token)
