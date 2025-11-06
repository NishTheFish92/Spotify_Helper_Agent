# Spotify Helper Agent

Lightweight CLI Spotify assistant that uses a LangChain-based agent and small utility tools to:
- create/delete playlists
- add/remove tracks
- fetch track recommendations (Last.fm)
- toggle or set playlist privacy
- look up Spotify track IDs

The project is intended for single-user, interactive use (opens a browser for Spotify OAuth).

---

## Contents

- src/ core app: auth, agent, utils  
- tools/ tool implementations used by the agent  
  - get_songs.py Last.fm recommender + fallback SERP description  
  - playlist_manipulation.py create/delete/get playlist id, privacy functions  
  - modify_songs_in_playlist.py add/delete songs in playlists  
- main.py entry point: authenticates, initializes LLM, runs the agent  
- user_id file created by the auth flow containing the Spotify user id (one-line)  
- pyproject.toml project metadata / build configuration

---

## Requirements

- Python 3.10+  
- Recommended packages (install with pip or your chosen installer):
  - langchain
  - langchain-community
  - requests
  - python-dotenv
  - serpapi (if using SERP fallback)
  - LLM provider client (openai, etc.)

---

## Installation
> It is advised to use the UV package manager for installing all requirements of this project due to its ease of use. Although, if you do not want to use UV, you can just do `pip install -r requirements.txt`.
1. Clone the repository.
```bash
git clone https://github.com/NishTheFish92/Spotify_Helper_Agent.git
```

2. Create a new virtual environment 
```bash
uv venv
```
3. Activate the virtual environment by doing

```bash
source .venv/bin/activate
``` 
In linux

OR
```powershell
.venv/Scripts/activate
```
In windows

4. Sync the requirements of the project to your newly created Virtual environment
```bash
uv sync
```
---

## Environment / .env

Create a `.env` file in the project root. Use the exact variable names the code expects:
> You will need to get the client_id and client_secret after creating a project from the spotify developer dashboard. The redirect URI must be set to `http://127.0.0.1:8888/callback/`. 

### Required environment variables
- client_id
- client_secret
- lastfm_api_key (for Last.fm recommendations)
- SERP_API_KEY (for SerpApi; used as the search fallback)
- GOOGLE_API_KEY (used specifically for Gemini/Google LLM integrations)
- refresh_token (Doing the OAuth process automatically adds this to your .env file)

Example `.env`:
```env
client_id=YOUR_SPOTIFY_CLIENT_ID
client_secret=YOUR_SPOTIFY_CLIENT_SECRET
redirect_uri=http://127.0.0.1:8888/callback/
# refresh_token=...      # automatically created by the auth flow 
lastfm_api_key=YOUR_LASTFM_KEY
SERP_API_KEY=YOUR_SERPAPI_KEY
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY  # for Gemini/Google LLM usage
```

Notes:
- The auth flow will append the refresh token to `.env`. Protect the `.env` file.
- The auth flow writes your Spotify user id into a file called `user_id` (single-line). The tools read `user_id` from that file.

---

## Quick start

1. Configure `.env` as shown above.
2. Run the app:
```bash
python main.py
```
Flow:
- `main_auth()` refreshes or obtains tokens via browser OAuth.
- On success `user_id` is written.
- `init_llm()` initializes your LLM client.
- `run_spotify_agent(llm)` starts the agent loop.

---

## Tools & usage notes

Agent-exposed tools return strings the LLM reads and follow simple input contracts:

- Create Playlist Input: playlist name (string)
- Delete Playlist Input: playlist name (string)
- Get Recommendations Input: `tag,limit` (single tag word and integer); returns newline-separated `Artist - Song`
- Get song IDs Input: list of song titles; returns spotify track IDs
- Add songs to playlist Input: Python-list-like string: `['trackid1',...,'playlist_name']`
- Delete songs from playlist same format as add
- Make playlist public / Make playlist private Input: playlist name (string)

Important:
- Access tokens expire you may need to re run `main.py` for every hour of usage to renew the access token.

---

## Potential updates
- Automatic refreshing of refresh token after Access token expires
- Multiple user support
- Better search recommendations
- Personalized Search recommendations
- Context aware between user messages.
- User interface

---

## References
1. https://docs.langchain.com/
2. https://developer.spotify.com/documentation/web-api
3. https://developer.spotify.com/dashboard
4. https://www.last.fm/api
5. https://serpapi.com/

