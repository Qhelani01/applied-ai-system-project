import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from src.recommender import load_songs, recommend_songs

st.set_page_config(
    page_title="VibeMatcher",
    page_icon="🎵",
    layout="wide",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .rec-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid #7c3aed;
    }
    .rec-rank { font-size: 1.6rem; font-weight: 800; color: #7c3aed; }
    .rec-title { font-size: 1.1rem; font-weight: 700; color: #f4f4f5; }
    .rec-artist { font-size: 0.9rem; color: #a1a1aa; }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-genre { background: #4c1d95; color: #ddd6fe; }
    .badge-mood  { background: #1e3a5f; color: #bae6fd; }
    .score-label { font-size: 0.75rem; color: #a1a1aa; margin-top: 8px; }
    .why-text { font-size: 0.82rem; color: #71717a; margin-top: 4px; }
    [data-testid="stSidebar"] { background: #13131f; }
</style>
""", unsafe_allow_html=True)

# ── Load catalog ──────────────────────────────────────────────────────────────
@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

songs = get_songs()

GENRES  = sorted({s["genre"] for s in songs})
MOODS   = sorted({s["mood"]  for s in songs})
MAX_SCORE = 5.8

PRESETS = {
    "— Custom —": None,
    "High-Energy Pop":    {"genre": "pop",        "mood": "happy",        "energy": 0.85, "tempo_bpm": 120},
    "Chill Lofi":         {"genre": "lofi",       "mood": "chill",        "energy": 0.35, "tempo_bpm": 80},
    "Deep Intense Rock":  {"genre": "rock",       "mood": "intense",      "energy": 0.90, "tempo_bpm": 145},
    "Relaxed Jazz":       {"genre": "jazz",       "mood": "relaxed",      "energy": 0.40, "tempo_bpm": 90},
    "Electronic Vibes":   {"genre": "electronic", "mood": "energetic",    "energy": 0.92, "tempo_bpm": 128},
    "⚠ High-Energy Sad":  {"genre": "indie pop",  "mood": "melancholic",  "energy": 0.95, "tempo_bpm": 110},
    "⚠ Acoustic Metal":   {"genre": "metal",      "mood": "dark",         "energy": 0.88, "tempo_bpm": 145},
    "⚠ Nonexistent Genre":{"genre": "dubstep",    "mood": "focused",      "energy": 0.75, "tempo_bpm": 130},
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎵 VibeMatcher")
    st.caption("Content-based music recommender")
    st.divider()

    preset = st.selectbox("Quick preset", list(PRESETS.keys()))
    p = PRESETS[preset]

    st.subheader("Your Taste Profile")

    genre = st.selectbox(
        "Favourite genre",
        GENRES + ([] if (p is None or p["genre"] in GENRES) else [p["genre"]]),
        index=(GENRES.index(p["genre"]) if p and p["genre"] in GENRES else 0),
    )

    mood_options = MOODS + ([] if (p is None or p["mood"] in MOODS) else [p["mood"]])
    mood = st.selectbox(
        "Favourite mood",
        mood_options,
        index=(mood_options.index(p["mood"]) if p and p["mood"] in mood_options else 0),
    )

    energy = st.slider(
        "Energy level",
        0.0, 1.0,
        value=float(p["energy"]) if p else 0.6,
        step=0.05,
        help="0 = very calm · 1 = maximum intensity",
    )

    tempo = st.slider(
        "Tempo (BPM)",
        60, 180,
        value=int(p["tempo_bpm"]) if p else 100,
        step=5,
    )

    k = st.slider("Number of recommendations", 1, 10, 5)

    st.divider()
    run = st.button("Find my songs ▶", use_container_width=True, type="primary")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🎵 VibeMatcher")
st.caption("A transparent music recommender — see exactly *why* each song was chosen.")

if not run:
    st.info("Set your taste profile in the sidebar and click **Find my songs ▶**")
    with st.expander("How scoring works"):
        st.markdown("""
| Criterion | Max points | Formula |
|-----------|-----------|---------|
| Genre match | **+2.0** | Exact match only |
| Mood match | **+1.0** | Exact match only |
| Energy similarity | **0 – 1.5** | `1.5 × (1 − |user_energy − song_energy|)` |
| Tempo similarity | **0 – 0.5** | `0.5 × (1 − |BPM_diff| / 200)` |
| **Total possible** | **5.8** | |

> **Bias note:** The +2.0 genre bonus dominates — users who like rare genres (metal, reggae, classical)
> always get the same song, regardless of energy or mood preferences.
        """)
    st.stop()

user_prefs = {"genre": genre, "mood": mood, "energy": energy, "tempo_bpm": tempo}
results = recommend_songs(user_prefs, songs, k=k)

# ── Profile summary ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Genre", genre.title())
col2.metric("Mood", mood.title())
col3.metric("Energy", f"{energy:.0%}")
col4.metric("Tempo", f"{tempo} BPM")

st.divider()

if not results:
    st.warning("No recommendations found.")
    st.stop()

avg_conf = sum(r[3] for r in results) / len(results)
top_score = results[0][1]

m1, m2, m3 = st.columns(3)
m1.metric("Top match score", f"{top_score:.2f} / {MAX_SCORE}")
m2.metric("Avg confidence", f"{avg_conf:.0%}")
m3.metric("Songs in catalog", len(songs))

st.subheader(f"Top {len(results)} recommendations for you")

# ── Recommendation cards ──────────────────────────────────────────────────────
for rank, (song, score, explanation, confidence) in enumerate(results, 1):
    score_pct   = score / MAX_SCORE
    conf_colour = "#22c55e" if confidence >= 0.7 else "#f59e0b" if confidence >= 0.5 else "#ef4444"

    st.markdown(f"""
    <div class="rec-card">
      <span class="rec-rank">#{rank}</span>
      <span class="rec-title" style="margin-left:10px">{song['title']}</span>
      <span class="rec-artist"> — {song['artist']}</span><br>
      <span class="badge badge-genre">{song['genre']}</span>
      <span class="badge badge-mood">{song['mood']}</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<p class="score-label">Match score</p>', unsafe_allow_html=True)
        st.progress(score_pct, text=f"{score:.2f} / {MAX_SCORE}")
        st.markdown('<p class="score-label">Confidence</p>', unsafe_allow_html=True)
        st.progress(float(confidence), text=f"{confidence:.0%}")
        st.markdown(f'<p class="why-text">Why: {explanation}</p>', unsafe_allow_html=True)
    with c2:
        st.metric("Energy",       f"{song['energy']:.0%}")
        st.metric("Danceability", f"{song['danceability']:.0%}")
        st.metric("Acousticness", f"{song['acousticness']:.0%}")

# ── Score chart ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Score comparison")

import pandas as pd
chart_data = pd.DataFrame({
    "Song": [f"#{i+1} {r[0]['title']}" for i, r in enumerate(results)],
    "Score": [r[1] for r in results],
    "Confidence": [r[3] for r in results],
})
st.bar_chart(chart_data.set_index("Song")[["Score", "Confidence"]])
