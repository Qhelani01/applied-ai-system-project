# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatcher 1.0**

---

## 2. Intended Use  

VibeMatcher recommends songs from a 18-song catalog based on a user's three core preferences: favorite genre, favorite mood, and target energy level (0-1 scale, where 1 is very intense). The system uses a content-based filtering approach (comparing song features to user preferences) and is designed for **educational exploration only, not real production use**. It assumes users can articulate their preferences and that similarity in these three dimensions predicts satisfaction.

---

## 3. How the Model Works  

VibeMatcher scores each song by comparing it to the user's stated preferences. **Genre and mood are exact-match features**—if a song's genre perfectly matches the user's favorite, it gets +2.0 points; if the mood matches, +1.0 point. **Energy is a similarity feature**—the system calculates how close the song's energy is to the user's target energy, with a maximum bonus of 1.5 points (closer matches earn more points). The system also applies small bonuses for tempo similarity and musical qualities like valence (how "happy" the song sounds). All songs are scored this way, then ranked from highest to lowest, and the user sees the top-5 recommendations with explanations of why each song scored as it did.

---

## 4. Data  

The catalog contains **18 songs** spanning 15 different genres: lofi (3 songs, 16.7%), pop (2 songs), and 13 other genres with 1 song each (rock, jazz, metal, reggae, classical, electronic, hip-hop, country, r&b, ambient, synthwave, indie pop, indie rock). **Critical limitation**: The catalog is extremely small, which means rare genres (metal, reggae, classical, etc.) have no variety—a metal fan always gets the same single metal song, regardless of other preferences. The dataset also skews toward high-energy music (mean energy = 0.64, median = 0.72), with only 5 songs below energy 0.4, creating a gap for users who want quiet, chill music.

---

## 5. Strengths  

The system works exceptionally well for **lofi and pop fans** because these genres are well-represented (5 songs combined). Exact-match recommendations—where genre, mood, and energy all align—are highly accurate and feel musically intuitive (e.g., a user wanting pop + happy + high energy gets "Sunrise City," which perfectly fits). The algorithm gracefully handles edge cases like nonexistent genres by falling back to mood and energy similarity. Transparent scoring explanations help users understand *why* each song was recommended, building trust in the system.

---

## 6. Limitations and Bias 

**Filter Bubble for Rare Genres**: Users who prefer metal, reggae, country, classical, or r&b music are trapped in a single-song loop—the catalog has only one song per genre. The +2.0 point genre bonus means these users will always see the same top recommendation regardless of mood or energy variations, creating a severe "filter bubble" with zero diversity. **Lofi Overrepresentation**: With 16.7% of the catalog dedicated to lofi, lofi fans receive abundant, high-quality recommendations while other genres are starved for representation. This mathematically biases the system *toward* lofi listeners. **High-Energy Bias**: The dataset contains 9/18 songs with energy > 0.7, but only 5 songs with energy ≤ 0.4. This creates a "low-energy gap"—users seeking calm, meditative, or relaxing music face a constrained choice set, while high-energy users enjoy abundant variety. **Mood Inflexibility**: The system requires exact mood matches, so requesting "energetic" will not suggest "playful" songs even though both moods convey positivity and joy. This rigidity prevents the system from handling mood synonyms or user preference ambiguity. **Energy Gap Vulnerability**: Users with extreme energy preferences (e.g., 0.05 or 0.95) receive poor recommendations because they're forced to accept severe energy mismatches just to stay within a preferred genre.

---

## 7. Evaluation  

I tested the system across 11 distinct user profiles: 5 standard personas (High-Energy Pop, Chill Lofi, Deep Intense Rock, Relaxed Jazz, Electronic Vibes) and 6 adversarial edge-case profiles (High-Energy Sad, Acoustic Metal, Extreme Low Energy, Rare Mood+Genre Combo, Happy Metal, Nonexistent Genre). Standard profiles received highly accurate, musically intuitive recommendations that matched my expectations. However, adversarial profiles exposed critical weaknesses: (1) rare-genre fans saw zero diversity, (2) conflicting mood+energy preferences were handled poorly by the algorithm, (3) users outside the high-energy mainstream were underserved. I also ran a weight-shift experiment (doubling energy importance to 3.0 points, halving genre to 1.0) which improved handling of conflicting preferences but sacrificed genre coherence, suggesting the original weights were well-balanced.

---

## 8. Future Work  

To improve VibeMatcher, I would:
- **Expand the dataset** to at least 50–100 songs per genre, eliminating single-song filter bubbles
- **Add mood fuzzy-matching** (e.g., treat "energetic" and "playful" as similar) to handle user ambiguity
- **Implement mood-based energy expectations** (e.g., reduce the energy mismatch penalty if the song's mood is known to vary widely in energy)
- **Rebalance the scoring** to penalize extreme energy gaps rather than just reward matches (e.g., if a user wants 0.1 energy but a song is 0.95, apply a penalty)
- **Add diversity-aware ranking** that prevents the same song from appearing at the top for multiple users, encouraging exploration
- **Track user feedback** to measure whether recommendations actually led to positive listening experiences, not just score matches

---

## 9. Personal Reflection  

Building this system taught me that **simple scoring rules can embed unexpected biases**. I designed the +2.0 genre bonus to keep recommendations coherent, but it inadvertently created a filter bubble for rare genres. The dataset size (18 songs) revealed how small catalogs amplify biases—there's no "tail" of niche recommendations to balance the dominant genres. This mirrors real-world recommendation systems: Spotify likely overrepresents mainstream genres simply because they have more songs to choose from, which mathematically advantages mainstream users. I also learned that **transparency matters**—by showing the user exactly how each song scored, I can help them understand and potentially challenge the system's assumptions. Finally, adversarial testing proved invaluable; testing only "normal" users would have hidden these biases entirely.
  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
