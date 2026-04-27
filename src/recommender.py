from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """Load songs from CSV, converting numerical fields to float/int.
    
    Returns:
        List of song dictionaries with validated numerical fields.
        
    Raises:
        FileNotFoundError: If CSV file not found.
        ValueError: If song data is invalid or missing required fields.
    """
    try:
        logger.info(f"Loading songs from {csv_path}...")
        songs = []
        required_fields = ['id', 'title', 'artist', 'genre', 'mood', 'energy', 
                          'tempo_bpm', 'valence', 'danceability', 'acousticness']
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Validate required fields exist
                    for field in required_fields:
                        if field not in row or row[field].strip() == '':
                            raise ValueError(f"Missing or empty field '{field}' in row {row_num}")
                    
                    # Convert numerical fields with validation
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
                    
                    # Validate energy values are in valid range [0, 1]
                    for field in ['energy', 'valence', 'danceability', 'acousticness']:
                        if not (0 <= song[field] <= 1):
                            logger.warning(f"Row {row_num}: {field} value {song[field]} out of range [0, 1]")
                    
                    songs.append(song)
                    
                except ValueError as e:
                    logger.error(f"Error parsing row {row_num}: {str(e)}")
                    raise
        
        logger.info(f"✓ Successfully loaded {len(songs)} songs")
        return songs
        
    except FileNotFoundError:
        logger.error(f"File not found: {csv_path}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading songs: {str(e)}")
        raise

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str], float]:
    """Score a song based on user preferences, returning (score, reasons, confidence).
    
    Args:
        user_prefs: User preferences dictionary with genre, mood, energy, etc.
        song: Song dictionary with features
        
    Returns:
        Tuple of (score, reasons_list, confidence_score)
        - score: 0-5.8 numeric score
        - reasons_list: list of strings explaining the score
        - confidence: 0-1 confidence in recommendation (based on match quality)
    """
    try:
        score = 0.0
        reasons = []
        confidence_factors = []  # Track what contributed to confidence

        # Genre match: +2.0 points (primary factor for confidence)
        if song['genre'].lower() == user_prefs['genre'].lower():
            score += 2.0
            reasons.append("genre match (+2.0)")
            confidence_factors.append(1.0)  # Perfect genre match = high confidence
        else:
            confidence_factors.append(0.0)  # No genre match reduces confidence

        # Mood match: +1.0 point (secondary factor for confidence)
        if song['mood'].lower() == user_prefs['mood'].lower():
            score += 1.0
            reasons.append("mood match (+1.0)")
            confidence_factors.append(1.0)  # Perfect mood match
        else:
            confidence_factors.append(0.5)  # Mood mismatch slightly reduces confidence

        # Energy similarity: 0-1.5 points (tertiary factor)
        # Formula: 1.5 × (1 - |user_energy - song_energy|)
        target_energy = user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = 1.5 * (1 - energy_diff)
        score += energy_score
        reasons.append(f"energy match ({energy_score:.2f})")
        # Energy similarity confidence: higher if match is close
        energy_confidence = 1.0 - energy_diff  # Close match = high confidence
        confidence_factors.append(energy_confidence)

        # Tempo similarity bonus: 0-0.5 points (optional)
        if 'tempo_bpm' in user_prefs:
            target_tempo = user_prefs['tempo_bpm']
            tempo_diff = abs(song['tempo_bpm'] - target_tempo)
            tempo_score = max(0, 0.5 * (1 - tempo_diff / 200))
            if tempo_score > 0.05:  # Only include if meaningful
                score += tempo_score
                reasons.append(f"tempo similarity ({tempo_score:.2f})")
                tempo_confidence = tempo_score / 0.5  # Normalize to 0-1
                confidence_factors.append(tempo_confidence)

        # Valence bonus for mood alignment (optional)
        if 'mood_characteristics' in user_prefs:
            mood = user_prefs['mood'].lower()
            valence = song['valence']
            # Happy moods benefit from high valence
            if mood in ['happy', 'energetic', 'playful'] and valence > 0.7:
                valence_bonus = 0.3
                score += valence_bonus
                reasons.append(f"valence alignment (+{valence_bonus})")
                confidence_factors.append(0.8)
            # Chill moods benefit from low valence
            elif mood in ['chill', 'relaxed', 'focused', 'contemplative'] and valence < 0.6:
                valence_bonus = 0.3
                score += valence_bonus
                reasons.append(f"valence alignment (+{valence_bonus})")
                confidence_factors.append(0.8)

        # Calculate overall confidence as weighted average of factors
        # Weight: genre (40%) > mood (30%) > energy (20%) > others (10%)
        if len(confidence_factors) >= 3:
            # We have genre, mood, and energy at minimum
            other_confidence = 0.0
            if len(confidence_factors) > 3:
                other_confidence = (sum(confidence_factors[3:]) / len(confidence_factors[3:])) * 0.1
            
            confidence = (
                confidence_factors[0] * 0.4 +  # genre weight
                confidence_factors[1] * 0.3 +  # mood weight
                confidence_factors[2] * 0.2 +  # energy weight
                other_confidence  # others weight
            )
        else:
            confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0

        # Log recommendations with low confidence
        if confidence < 0.5:
            logger.warning(f"Low confidence recommendation: {song['title']} (confidence: {confidence:.2f})")

        return score, reasons, min(confidence, 1.0)  # Clamp confidence to [0, 1]

    except Exception as e:
        logger.error(f"Error scoring song {song.get('title', 'Unknown')}: {str(e)}")
        return 0.0, ["error scoring song"], 0.0

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str, float]]:
    """Return top-k songs ranked by score for the given user preferences.
    
    Returns:
        List of tuples (song, score, explanation, confidence)
    """
    try:
        if not songs:
            logger.warning("No songs available for recommendation")
            return []
        
        def score_with_explanation(song):
            """Helper: score a song and format the explanation"""
            score, reasons, confidence = score_song(user_prefs, song)
            return (song, score, ", ".join(reasons), confidence)

        results = sorted(
            map(score_with_explanation, songs),
            key=lambda x: x[1],
            reverse=True
        )[:k]
        
        logger.info(f"Generated {len(results)} recommendations with average confidence: "
                   f"{sum(r[3] for r in results) / len(results):.2f}" if results else "No results")
        
        return results
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return []
