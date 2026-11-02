import requests
import os
from dotenv import load_dotenv
from src import retrieve_access_token
from langchain_core.tools import tool
from .playlist_manipulation import get_playlist_id



@tool(parse_docstring=True)
def add_songs_to_playlist(song_ids: list[str], playlist_name: str):
    """
    Add songs to playlist.

    Args:
        song_ids (list[str]): Spotify track IDs to add
        playlist_name (str): Name of the playlist to add them to

    Returns:
        str: Success or failure
    """
    access_token = retrieve_access_token()
    playlist_id = get_playlist_id(playlist_name)
    if(playlist_id is None):
        return(f"Playlist - {playlist_name} does not exist in user library!")
    uris = [f"spotify:track:{tid}" for tid in song_ids]
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
@tool(parse_docstring=True)
def delete_songs_from_playlist(song_ids: list[str], playlist_name: str):
    """
    Delete specific songs from a playlist.

    Args:
        song_ids (list[str]): Spotify track IDs to delete
        playlist_name (str): Name of the playlist to delete them from

    Returns:
        str: Success or failure message
    """
    access_token = retrieve_access_token()
    playlist_id = get_playlist_id(playlist_name)
    if playlist_id is None:
        return f"Playlist - {playlist_name} does not exist in user library! Abort deletiion as playlist does not exist."

    uris = [{"uri": f"spotify:track:{tid}"} for tid in song_ids]
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

