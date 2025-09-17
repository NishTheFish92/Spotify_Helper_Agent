import requests
import json
from src import retrieve_access_token

with open("user_id", "r") as f:
    user_id = f.read().strip()

def create_playlist(name : str):
    """Creates a playlist with specified name Input format: 'name'"""
    access_token = retrieve_access_token()
    playlist_data = {
        "name": name,
        "public": False
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists",
                        headers=headers, data=json.dumps(playlist_data))
        r.raise_for_status()
        return(f"Success Playlist {name} created ")
    except:
        return(f"Failure ({r.status_code}): {r.text} ")
