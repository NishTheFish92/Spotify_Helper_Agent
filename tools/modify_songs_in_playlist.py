import requests
import os
from dotenv import load_dotenv
import ast
from src import retrieve_access_token
from .playlist_manipulation import get_playlist_id



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
    if response.status_code in [200,201]:
        return("Tracks added successfully!")
    else:
        return("Error:", response.status_code, response.text)


#Delete songs from specific playlist(Very similar to add_songs_to_playlist).
def delete_songs_from_playlist(input_str: str):
    """
    Delete specific songs from a playlist.
    Args:
        input_str (str): List of track IDs followed by playlist name
    Returns:
        str: Success or failure message
    """
    access_token = retrieve_access_token()
    songs = ast.literal_eval(input_str)
    playlist_name = songs.pop()
    playlist_id = get_playlist_id(playlist_name)
    if playlist_id is None:
        return f"Playlist - {playlist_name} does not exist in user library! Abort deletiion as playlist does not exist."

    uris = [{"uri": f"spotify:track:{tid}"} for tid in songs]
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"tracks": uris}
    response = requests.delete(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        return "Tracks deleted successfully!"
    else:
        return f"Error: {response.status_code}, {response.text}"

