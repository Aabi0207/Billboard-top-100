import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

# Scraping Billboard 100

print("Welcome to the Music Time Machine!")
date = input("Enter the date you want to travel to (YYYY-MM-DD): ")
URL = f"https://www.billboard.com/charts/hot-100/{date}/"
response = requests.get(URL)
billboard_data = response.text
soup = BeautifulSoup(billboard_data, "html.parser")
songs = soup.find_all(name="h3", id="title-of-a-story", class_="u-line-height-125")
song_titles = [title.getText().strip("\n\t") for title in songs]
artists = soup.find_all(name="span", class_="u-max-width-330")
artist_names = [name.getText().strip("\n\t") for name in artists]
song_and_artist = dict(zip(song_titles, artist_names))

print(song_and_artist)
print()
print("Searching for songs on Spotify and creating new playlist...")

# Spotify Authentication

OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIPY_CLIENT_ID = SPOTIFY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI = "http://example.com"
SPOTIPY_SCOPE = "playlist-modify-private"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIPY_SCOPE,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)

# Search Spotify for songs by title and artist

song_uris = []
for (song, artist) in song_and_artist.items():
    try:
        result = sp.search(q=f"track:{song} artist:{artist}", type="track")
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except:
        pass

print(f"Number of songs found: {len(song_uris)}")

# Create a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False, )
print(playlist)

# Add songs found into new playlist

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print(f"New playlist '{date} Billboard 100' successfully created on Spotify!")
