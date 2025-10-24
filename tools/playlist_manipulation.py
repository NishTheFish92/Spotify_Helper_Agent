import requests
import json
from src import retrieve_access_token

with open("user_id", "r") as f:
    user_id = f.read().strip()

def get_playlist_id(name):
    """
    Gets the playlist ID from the playlist name
    Args:
        str : Playlist name
    Returns:
        str: Playlist ID
    """
    access_token = retrieve_access_token()
    playlist_id = None
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 50, "offset": 0}
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return f"something went wrong! {response.status_code}"

        data = response.json()
        for playlist in data.get("items", []):
            if playlist["name"].lower() == name.lower():
                playlist_id = playlist["id"]

        if data.get("next"):
            url = data["next"]
            params = None
        else:
            break
    return(playlist_id)

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

#Delete playlist with given playlist name
def delete_playlist(name: str):
    """Deletes a playlist with the given name"""
    access_token = retrieve_access_token()
    playlist_id = get_playlist_id(name)
    if playlist_id is None:
        return f"Playlist - '{name}' not found! Abort Deletion."

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/followers"

    r = requests.delete(url, headers=headers)
    if r.status_code == 200:
        return f"Playlist - '{name}' deleted successfully."
    else:
        return f" Error ({r.status_code}): {r.text}"

#Change playlist from private to public and public to private
def toggle_playlist_privacy(name: str):
    """Changes playlist visibility (private ↔ public)"""
    access_token = retrieve_access_token()
    playlist_id = get_playlist_id(name)
    if playlist_id is None:
        return f"Playlist - '{name}' not found."

    # Get current playlist details
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return f"Error fetching playlist info: ({r.status_code}) {r.text}"

    current_status = r.json().get("public", False)
    new_status = not current_status  # Toggle

    update_data = {"public": new_status}
    headers["Content-Type"] = "application/json"

    r = requests.put(url, headers=headers, data=json.dumps(update_data))
    if r.status_code == 200:
        visibility = "public" if new_status else "private"
        return f"Playlist '{name}' is now {visibility}."
    else:
        return f"Error updating playlist: ({r.status_code}) {r.text}"
