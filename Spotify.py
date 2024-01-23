import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import os  # Added import for os module

# Set up Spotify authentication
SPOTIPY_CLIENT_ID = '239d61c551784897b20019adc0c4660e'
SPOTIPY_CLIENT_SECRET = 'b02abecfbb9847cebbdf00a42568b0f0'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8081'

# Modify the scope based on your requirements
scope = 'user-library-read playlist-read-private'

# Use SpotifyOAuth for authentication
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope)

# Get user authorization token
token = sp_oauth.get_access_token(as_dict=False)  # as_dict=False to get the token string directly

# Create Spotify client with the obtained token
sp = spotipy.Spotify(auth=token)

# Function to get top tracks for a given genre
def get_top_tracks_for_genre(genre, limit=10):
    try:
        # Get recommendations based on the specified genre
        recommendations = sp.recommendations(seed_genres=[genre], limit=limit)
        top_tracks = recommendations['tracks']
        return top_tracks
    except Exception as e:
        print(f"Error fetching top tracks for genre '{genre}': {e}")
        return None

# Function to save tracks to a CSV file
def save_tracks_to_csv(tracks, mood):
    if tracks:
        track_list = []
        for idx, track in enumerate(tracks):
            track_data = {
                'Name': track['name'],
                'Album': track['album']['name'],
                'Artists': ', '.join(artist['name'] for artist in track['artists'])
            }
            track_list.append(track_data)

        # Create 'top_tracks' directory if it doesn't exist
        os.makedirs('top_tracks', exist_ok=True)

        # Create a DataFrame for the tracks
        df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artists'])

        # Save the DataFrame to a CSV file
        df.to_csv(f'top_tracks/{mood.lower()}_top_tracks.csv', index=False)
        print(f"Top 10 tracks for '{mood}' saved to CSV file.")
    else:
        print(f"No tracks found for '{mood}'")

# Define mood-related genres
mood_genres = {
    'angry': 'metal',
    'disgust': 'punk',
    'happy': 'pop',
    'neutral': 'ambient',
    'sad': 'blues',
    'surprise': 'jazz'
}

# Fetch and save top 10 tracks for each genre
for mood, genre_to_fetch in mood_genres.items():
    top_tracks = get_top_tracks_for_genre(genre_to_fetch)
    save_tracks_to_csv(top_tracks, mood)
    time.sleep(2)  # Add a small delay between requests to avoid rate limits
