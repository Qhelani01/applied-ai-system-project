from src.recommender import Song, UserProfile, Recommender, load_songs, score_song, recommend_songs
import pytest
import os

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


# ============================================================================
# OOP Interface Tests (Recommender class)
# ============================================================================

def test_recommend_returns_songs_sorted_by_score():
    """Test that recommendations are sorted by score, highest first."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    """Test that explanation generation works."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ============================================================================
# Functional Tests (score_song, recommend_songs)
# ============================================================================

def test_score_song_exact_genre_mood_match():
    """Test scoring with exact genre and mood match."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    # Should have genre (+2.0) + mood (+1.0) + energy (+1.5) = 4.5 minimum
    assert score >= 4.0
    assert confidence >= 0.8  # High confidence with exact matches
    assert "genre match" in str(reasons).lower()
    assert "mood match" in str(reasons).lower()


def test_score_song_no_genre_match():
    """Test scoring with genre mismatch."""
    user_prefs = {
        "genre": "rock",
        "mood": "happy",
        "energy": 0.8,
    }
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "lofi",  # Different genre
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    # Should not have genre bonus, confidence should be lower
    assert score < 4.0  # No genre match
    assert confidence < 0.8  # Lower confidence without genre match


def test_score_song_energy_similarity():
    """Test energy similarity scoring."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.5,  # Target mid-range energy
    }
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.5,  # Exact energy match
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    # Should include energy score around 1.5 (max)
    assert score >= 4.0  # Genre + mood + good energy
    assert any("energy" in str(r).lower() for r in reasons)


def test_score_song_returns_confidence_0_to_1():
    """Test that confidence score is always between 0 and 1."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    assert 0 <= confidence <= 1, "Confidence must be between 0 and 1"


def test_recommend_songs_returns_sorted_by_score():
    """Test that recommend_songs returns results sorted by score."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    songs = [
        {
            "id": 1,
            "title": "Perfect Pop",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.9,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        {
            "id": 2,
            "title": "Wrong Genre",
            "artist": "Artist B",
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "tempo_bpm": 145,
            "valence": 0.5,
            "danceability": 0.3,
            "acousticness": 0.1,
        },
    ]
    
    results = recommend_songs(user_prefs, songs, k=2)
    
    assert len(results) == 2
    assert results[0][0]["genre"] == "pop"  # Best match should be first
    assert results[0][1] > results[1][1]  # Scores should be descending


def test_recommend_songs_respects_k_limit():
    """Test that recommend_songs returns at most k results."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    songs = [
        {
            "id": i,
            "title": f"Song {i}",
            "artist": f"Artist {i}",
            "genre": "pop" if i % 2 == 0 else "rock",
            "mood": "happy",
            "energy": 0.5 + (i * 0.05),
            "tempo_bpm": 100 + i * 5,
            "valence": 0.7,
            "danceability": 0.6,
            "acousticness": 0.3,
        }
        for i in range(10)
    ]
    
    results = recommend_songs(user_prefs, songs, k=3)
    
    assert len(results) == 3


def test_recommend_songs_returns_confidence_scores():
    """Test that recommend_songs includes confidence scores."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    songs = [
        {
            "id": 1,
            "title": "Test Song",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.9,
            "danceability": 0.8,
            "acousticness": 0.2,
        }
    ]
    
    results = recommend_songs(user_prefs, songs, k=1)
    
    assert len(results) == 1
    song, score, explanation, confidence = results[0]
    assert 0 <= confidence <= 1


# ============================================================================
# Edge Case & Error Handling Tests
# ============================================================================

def test_score_song_with_missing_optional_fields():
    """Test scoring when optional fields are missing."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        # No tempo_bpm provided
    }
    song = {
        "id": 1,
        "title": "Test Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    # Should still score despite missing optional field
    assert score > 0
    assert confidence > 0


def test_score_song_extreme_energy_values():
    """Test scoring with extreme energy values (0 and 1)."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.0,  # Extremely low
    }
    song = {
        "id": 1,
        "title": "High Energy Song",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 1.0,  # Extremely high
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    
    score, reasons, confidence = score_song(user_prefs, song)
    
    # Should handle extreme values without crashing
    assert score >= 0
    assert confidence >= 0
    assert confidence <= 1


def test_recommend_songs_empty_list():
    """Test recommend_songs with empty song list."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    songs = []
    
    results = recommend_songs(user_prefs, songs, k=5)
    
    # Should return empty list, not crash
    assert results == []


def test_recommend_songs_fewer_songs_than_k():
    """Test when there are fewer songs than k."""
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }
    songs = [
        {
            "id": 1,
            "title": "Song 1",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.9,
            "danceability": 0.8,
            "acousticness": 0.2,
        }
    ]
    
    results = recommend_songs(user_prefs, songs, k=5)
    
    # Should return only 1 song, not error
    assert len(results) == 1


# ============================================================================
# Data Loading Tests
# ============================================================================

def test_load_songs_from_csv():
    """Test loading songs from CSV file."""
    csv_path = "data/songs.csv"
    
    # Only test if file exists
    if os.path.exists(csv_path):
        songs = load_songs(csv_path)
        
        assert len(songs) > 0
        assert all(isinstance(song, dict) for song in songs)
        assert all('id' in song for song in songs)
        assert all('genre' in song for song in songs)
        assert all('mood' in song for song in songs)


def test_load_songs_validates_numerical_ranges():
    """Test that loaded songs have valid numerical ranges."""
    csv_path = "data/songs.csv"
    
    if os.path.exists(csv_path):
        songs = load_songs(csv_path)
        
        for song in songs:
            # Energy, valence, danceability, acousticness should be 0-1
            assert 0 <= song['energy'] <= 1, f"Energy out of range: {song['energy']}"
            assert 0 <= song['valence'] <= 1, f"Valence out of range: {song['valence']}"
            assert 0 <= song['danceability'] <= 1, f"Danceability out of range: {song['danceability']}"
            assert 0 <= song['acousticness'] <= 1, f"Acousticness out of range: {song['acousticness']}"
