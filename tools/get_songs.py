import requests
import os
from dotenv import load_dotenv
import ast
from src import retrieve_access_token
load_dotenv()
API_KEY = os.getenv("lastfm_api_key")
recommendation_desc = """Gets song recommendations based on user mood or activity.
Input: 
- tag: a single word describing the user's mood or activity (e.g., "chill", "workout", "study")
- limit: number of songs to recommend (integer)
Always condense the user's request to a single tag and a number before calling this tool.
Input format: tag,limit
"""

def get_recommendations(input_str : str):
    """
    Fetches top tracks for a given mood tag from Last.fm.

    Returns:
        str: Formatted string with track and artist names.
    """
    parts = input_str.split(',')
    tag = parts[0]
    limit = int(parts[1])
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


def get_spotify_song_id(input_str : str):
    """
    gets spotify song IDs from song names

    Returns:
        str: List of IDs
    """
    access_token = retrieve_access_token()
    songs = ast.literal_eval(input_str)
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
    for i in songs:
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
