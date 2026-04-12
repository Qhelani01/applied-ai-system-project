from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV, converting numerical fields to float/int."""
    print(f"Loading songs from {csv_path}...")
    songs = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numerical fields
            song = {
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness']),
            }
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song based on user preferences, returning (score, reasons)."""
    score = 0.0
    reasons = []

    # Genre match: +2.0 points
    if song['genre'].lower() == user_prefs['genre'].lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    # Mood match: +1.0 point
    if song['mood'].lower() == user_prefs['mood'].lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy similarity: 0-1.5 points
    # Formula: 1.5 × (1 - |user_energy - song_energy|)
    target_energy = user_prefs.get('energy', 0.5)
    energy_diff = abs(song['energy'] - target_energy)
    energy_score = 1.5 * (1 - energy_diff)
    score += energy_score
    reasons.append(f"energy match ({energy_score:.2f})")

    # Tempo similarity bonus: 0-0.5 points (optional)
    if 'tempo_bpm' in user_prefs:
        target_tempo = user_prefs['tempo_bpm']
        tempo_diff = abs(song['tempo_bpm'] - target_tempo)
        tempo_score = max(0, 0.5 * (1 - tempo_diff / 200))
        if tempo_score > 0.05:  # Only include if meaningful
            score += tempo_score
            reasons.append(f"tempo similarity ({tempo_score:.2f})")

    # Valence bonus for mood alignment (optional)
    if 'mood_characteristics' in user_prefs:
        mood = user_prefs['mood'].lower()
        valence = song['valence']
        # Happy moods benefit from high valence
        if mood in ['happy', 'energetic', 'playful'] and valence > 0.7:
            valence_bonus = 0.3
            score += valence_bonus
            reasons.append(f"valence alignment (+{valence_bonus})")
        # Chill moods benefit from low valence
        elif mood in ['chill', 'relaxed', 'focused', 'contemplative'] and valence < 0.6:
            valence_bonus = 0.3
            score += valence_bonus
            reasons.append(f"valence alignment (+{valence_bonus})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return top-k songs ranked by score for the given user preferences."""
    def score_with_explanation(song):
        """Helper: score a song and format the explanation"""
        score, reasons = score_song(user_prefs, song)
        return (song, score, ", ".join(reasons))

    return sorted(
        map(score_with_explanation, songs),
        key=lambda x: x[1],
        reverse=True
    )[:k]
