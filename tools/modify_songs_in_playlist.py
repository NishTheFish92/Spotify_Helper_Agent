import requests
import os
from dotenv import load_dotenv
import ast
from src import retrieve_access_token


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

def add_songs_to_playlist(input_str: str):
    """
    Add songs to playlist.
    Returns:
        str: Success or failure
    """
    access_token = retrieve_access_token()
    songs = ast.literal_eval(input_str)
    playlist_name = songs.pop()
    playlist_id = get_playlist_id(playlist_name)
    if(playlist_id is None):
        return(f"Playlist - {playlist_name} does not exist in user library!")
    uris = [f"spotify:track:{tid}" for tid in songs]
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
    }
    data = {"uris": uris}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return("Tracks added successfully!")
    else:
        return("Error:", response.status_code, response.text)


#Delete songs from specific playlist(Very similar to add_songs_to_playlist).

