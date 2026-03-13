# Spotify Helper Agent

A conversational CLI tool that lets you manage your Spotify library using natural language. Built with LangChain and a Gemini/OpenAI backend, it handles playlist workflows end-to-end. Creating playlists, finding recommendations, and managing tracks without touching the Spotify UI.

**Built with:** Python · LangChain · Spotify Web API · Last.fm API · SerpAPI · Gemini/OpenAI

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
- Recommended packages (install via uv sync or pip install -r requirements.txt):
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
Linux/MacOS:
```bash
source .venv/bin/activate
``` 

Windows:
```powershell
.venv/Scripts/activate
```


4. Sync the requirements of the project to your newly created Virtual environment
```bash
uv sync
```
---

## Environment / .env

Create a `.env` file in the project root. Use the exact variable names the code expects:
> You will need to get the client_id and client_secret after creating a project from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard). The redirect URI must be set to `http://127.0.0.1:8888/callback/`. 

### Required environment variables
- client_id
- client_secret
- lastfm_api_key (for Last.fm recommendations)
- SERP_API_KEY (for SerpApi; used as the search fallback)
- GOOGLE_API_KEY (used specifically for Gemini/Google LLM integrations)
- refresh_token (Going through the OAuth process automatically adds this to your .env file)

Example `.env`:
```env
client_id=YOUR_SPOTIFY_CLIENT_ID
client_secret=YOUR_SPOTIFY_CLIENT_SECRET
# refresh_token=...      # automatically created by the auth flow 
lastfm_api_key=YOUR_LASTFM_KEY   # primary recommendations source (replaces deprecated Spotify /recommendations)
SERP_API_KEY=YOUR_SERPAPI_KEY    # fallback when Last.fm results are thin
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
> Known limitation: Access tokens expire after one hour. Re-run python main.py to refresh. Automatic token refresh is planned (see Roadmap).
> 
### A note on recommendations
Spotify's native `/recommendations` endpoint was deprecated in late 2024 and is 
no longer available to new or existing third-party apps. To work around this, the 
agent uses **Last.fm** as the primary recommendation source (via tag-based lookup) 
and falls back to **SerpAPI** (Google search) when Last.fm returns insufficient 
results. This is why both `lastfm_api_key` and `SERP_API_KEY` are required.

## Tools & usage notes

Agent-exposed tools return strings the LLM reads and follow simple input contracts:

| Tool | Input | Returns |
|------|-------|---------|
| Create Playlist | playlist name | confirmation string |
| Delete Playlist | playlist name | confirmation string |
| Get Recommendations | `tag,limit` | newline-separated `Artist - Song` |
| Get Song IDs | list of song titles | Spotify track IDs |
| Add Songs to Playlist | `['trackid1', ..., 'playlist_name']` | confirmation string |
| Remove Songs from Playlist | `['trackid1', ..., 'playlist_name']` | confirmation string |
| Make Playlist Public/Private | playlist name | confirmation string |





---

## Roadmap
- Automatic access token refresh (no need to re-run main.py hourly)
- Multi-user support
- Personalized and context-aware recommendations
- Conversation memory between user messages
- Optional web UI

---

## References
1. https://docs.langchain.com/
2. https://developer.spotify.com/documentation/web-api
3. https://developer.spotify.com/dashboard
4. https://www.last.fm/api
5. https://serpapi.com/

