import requests
import os
from dotenv import load_dotenv
from src import retrieve_access_token
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
load_dotenv()
API_KEY = os.getenv("lastfm_api_key")
search = SerpAPIWrapper()

@tool(parse_docstring=True)
def get_recommendations(tag: str, limit: int):
    """
    Gets song recommendations for a mood or activity tag from Last.fm.

    Args:
        tag (str): A single word describing the mood or activity (e.g. "chill", "workout")
        limit (int): Number of songs to recommend

    Returns:
        str: Formatted string with track and artist names.
    """
    url = 'https://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'tag.getTopTracks',
        'tag': tag,
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit
    }

    response = requests.get(url, params=params)
    status = response.status_code  # Get the status code
    if status != 200:
        return f"Failed to fetch recommendations. Status code: {status}. Response: {response.text}"

    data = response.json()

    recommendations = []
    for track in data.get('tracks', {}).get('track', []):
        track_name = track['name']
        artist_name = track['artist']['name']
        recommendations.append(f"{track_name} - {artist_name}")
    
    if recommendations:
       return recommendations
    else:
       return f"No recommendations found for this tag. (Status code: {status})"


@tool(parse_docstring=True)
def search_songs(query: str):
    """
    Searches the web for songs matching a query (e.g. "top 10 chill songs").

    Args:
        query (str): What to search for

    Returns:
        str: Search results containing song names
    """
    return search.run(query)


@tool(parse_docstring=True)
def get_spotify_song_id(song_names: list[str]):
    """
    Looks up Spotify track IDs for the given song names. Songs that aren't found are skipped.

    Args:
        song_names (list[str]): Song names, each in the format "Artist - Song"

    Returns:
        str: List of IDs
    """
    access_token = retrieve_access_token()
    headers = {
    "Authorization": f"Bearer {access_token}"
    }
    params = {
    "q": "",
    "type": "track",
    "limit": 1
    }
    ids = []
    url = "https://api.spotify.com/v1/search"
    for i in song_names:
        params['q'] = i
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("tracks", {}).get("items", [])
            if items:
                track_id = items[0]["id"]
                ids.append(track_id)
            else:
                pass
        else:
            print(f"something went wrong {response.status_code}, {response.text}")
    return(ids)
