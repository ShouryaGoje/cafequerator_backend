import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np

# Define Spotify API credentials (Replace these with your actual credentials)
CLIENT_ID = "44c18fde03114e6db92a1d4deafd6a43"
CLIENT_SECRET = "645c1dfc9c7a4bf88f7245ea5d90b454"
REDIRECT_URI = "http://localhost:5173"
SCOPE = "user-library-read playlist-read-private"  # Scope required for accessing playlist data

# Initialize Spotify API client with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Function to fetch audio features of a track
def get_audio_features(track_id):
    features = sp.audio_features(track_id)
    if features and features[0]:
        return features[0]
    else:
        print(f"Error: No audio features found for track ID {track_id}")
        return None


# Function to compare two values within a percentage threshold
def compare_features(track_value, comparison_value, threshold_percentage):
    lower_bound = track_value - (track_value * threshold_percentage)
    upper_bound = track_value + (track_value * threshold_percentage)
    return lower_bound <= comparison_value <= upper_bound

# Function to compare all the audio features
def compare_tracks(track_features, comparison_features, thresholds):
    if comparison_features is None:
        print("Error: Comparison track features not available.")
        return 0  # No similarity, return 0 similarity
    
    similarity_count = 0
    features = [
        'acousticness', 'danceability', 'energy', 'key', 'instrumentalness',
        'loudness', 'mode', 'tempo', 'time_signature', 'valence'
    ]
    
    for feature in features:
        track_value = track_features[feature]
        comparison_value = comparison_features[feature]
        threshold_percentage = thresholds[feature]
        
        if compare_features(track_value, comparison_value, threshold_percentage):
            similarity_count += 1
    
    # Calculate similarity as a percentage of matching features
    similarity_percentage = (similarity_count / len(features)) * 100
    return similarity_percentage


# Function to fetch playlist tracks
def fetch_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return [(track['track']['id'], track['track']['name'], track['track']['artists'][0]['name']) for track in results['items']]

# Main function to fetch playlist and compare tracks with comparison track
def check_playlist_vibe(playlist_id, comparison_track_id, thresholds):
    # Fetch playlist tracks
    playlist_tracks = fetch_playlist_tracks(playlist_id)
    comparison_features = get_audio_features(comparison_track_id)

    if comparison_features is None:
        print("Comparison track features are not available, exiting comparison.")
        return
    
    # Store similarity percentages for each track
    matching_tracks = 0
    for track_id, track_name, artist_name in playlist_tracks:
        track_features = get_audio_features(track_id)
        if track_features is None:
            print(f"Skipping track {track_name} by {artist_name} due to missing audio features.")
            continue

        similarity_percentage = compare_tracks(track_features, comparison_features, thresholds)
        print(f"Track: {track_name} by {artist_name} - Similarity: {similarity_percentage}%")
    
    for track in playlist_tracks:
        # Check if the track is a dictionary or tuple and extract the track ID accordingly
        if isinstance(track, dict):
            track_id = track['id']  # If the track is a dictionary, access by key
        elif isinstance(track, tuple):
            track_id = track[0]  # If the track is a tuple, access by index (assuming ID is at index 0)
        else:
            print("Unknown track structure:", track)
            continue
        
        # Fetch the audio features for the track
        track_features = get_audio_features(track_id)
        
        if track_features is None:
            continue
        
        # Compare the features
        similarity_percentage = compare_tracks(track_features, comparison_features, thresholds)
        
        # Check if similarity is greater than or equal to 50%
        if similarity_percentage >= 50:
            matching_tracks += 1

    # Calculate threshold of matching tracks (50% of total playlist)
    total_tracks = len(playlist_tracks)
    threshold = total_tracks * 0.5  # 50% of total tracks

    if matching_tracks >= threshold:
        print("This playlist matches the vibe of the comparison track.")
    else:
        print("This playlist does not match the vibe of the comparison track.")



# Define the percentage thresholds for each feature
thresholds = {
    'acousticness': 0.40,
    'danceability': 0.40,
    'energy': 0.40,
    'key': 0.10,
    'instrumentalness': 0.40,
    'loudness': 0.20,
    'mode': 0.00,  # Special case for mode (exact match)
    'tempo': 0.20,
    'time_signature': 0.25,
    'valence': 0.20
}

# Example usage
playlist_id = '7pmde8yDXHlDDRX4v5uUuJ'  # Replace with your playlist ID
comparison_track_id = '78BWCd70D1X6LMkDZm1UoF'  # Replace with your comparison track ID
check_playlist_vibe(playlist_id, comparison_track_id, thresholds)
