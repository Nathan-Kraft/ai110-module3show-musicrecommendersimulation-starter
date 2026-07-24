# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

Real-world music recommenders (Spotify, Apple Music, etc.) typically blend two approaches: content-based filtering, which matches a song's own attributes (genre, tempo, mood, acoustic qualities) against a listener's stated or inferred tastes, and collaborative filtering, which looks at what similar users listened to and recommends based on those patterns, even without knowing why a song fits. Production systems also weigh signals we're not using here, like skip rates, replay counts, time of day, and social trends, and they constantly re-rank based on real-time feedback rather than a single static formula.

My version is a simplified, transparent content-based recommender. It has no listening history or other users to learn from, so it relies entirely on explicit song attributes and a stated user profile. We prioritize clarity over sophistication: every recommendation traces back to a clear, human-readable reason, such as a matched genre, matched mood, or close energy, tempo, and acoustic fit. The weighting reflects a deliberate choice about what matters most to a listener, putting genre identity first, mood second, and then numeric closeness on energy, tempo, and acoustic feel. It won't discover surprising picks the way collaborative filtering can, but it will always be able to justify its choices in plain language. 

**Scoring rule**: each song is scored on a 0–1 scale:

    score = (0.35 × genre_match)
          + (0.25 × mood_match)
          + (0.20 × energy_closeness)
          + (0.10 × tempo_closeness)
          + (0.10 × acoustic_alignment)

- **genre_match / mood_match**: `1` if the song matches the user's favorite genre/mood, else `0`
- **energy_closeness**: `1 - |song.energy - target_energy|` (energy is already 0–1)
- **tempo_closeness**: `1 - min(|song.tempo_bpm - target_tempo| / 160, 1)`, normalized against an assumed 40–200 bpm range; skipped if the user has no tempo preference
- **acoustic_alignment**: `acousticness` if the user likes acoustic songs, else `1 - acousticness`

Genre outweighs mood so a user's core genre identity still surfaces even when their mood target isn't hit; energy is the strongest numeric "vibe" signal, so it outweighs tempo and acoustic fit.

**Scope decision:** the catalog also includes `valence` and `danceability` for each song, but this version's `UserProfile` has no corresponding preference fields for them, so they are not used in scoring. This was a deliberate choice to keep the scoring rule simple and easy to explain rather than an oversight. A natural next step would be adding `target_valence`/`likes_danceable` preferences and folding them into the score.

**Ranking rule**: sort all songs by score descending, break ties by song `id` ascending, return the top `k`.

**Display note**: the internal score stays on a 0–1 scale for the math above, but when a score is shown to the user it is multiplied by 100 and rounded (e.g., an internal score of `0.87` displays as `87/100`). This keeps the ranking math clean while making the output feel more intuitive to read.

### Algorithm Recipe (Finalized)

1. For each song in the catalog, compute:

       score = (0.35 × genre_match)
             + (0.25 × mood_match)
             + (0.20 × energy_closeness)
             + (0.10 × tempo_closeness)
             + (0.10 × acoustic_alignment)

2. Sort all scored songs by `score` descending, breaking ties by `id` ascending.
3. Return the top `k` songs, along with a plain-language explanation built from whichever match/closeness terms contributed most (e.g., "matches your favorite genre" or "energy is close to what you want").
4. When displaying a score, multiply the 0–1 value by 100 and round to the nearest whole number.

### Potential Biases

- **Genre/mood dominance**: because genre and mood together make up 60% of the score, a user profile with an unusual genre/mood combination (e.g., "ambient" + "intense", which doesn't appear in the catalog) will score every song lower across the board, making recommendations feel flatter and less differentiated for that user.
- **Catalog imbalance**: the sample catalog has only 10 songs and just 1–2 per genre/mood combination. Users whose taste matches an underrepresented genre (e.g., jazz, ambient) have far fewer candidates to be recommended, regardless of how well the scoring works.
- **Assumed tempo range**: the 40–200 bpm normalization range is a judgment call. If the actual catalog skews narrower (as it does here, ~60–152 bpm), tempo_closeness scores compress toward the high end and the term contributes less differentiation than its 0.10 weight suggests.
- **No personalization over time**: the system has no memory of past recommendations or feedback, so it will keep suggesting the same top songs to the same user profile indefinitely, and can't learn from what a user actually likes versus what they stated in their profile.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app (from the project root, so the `data/songs.csv` path resolves):

```bash
python src/main.py
```

### Running Tests

Run the starter tests with:

```bash
python -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Ran with the starter profile in `main.py` (`genre=pop, mood=happy, energy=0.8`) against the 20-song catalog:

```
Loaded songs: 20

Top recommendations:

1. Sunrise City (Neon Echo) - Score: 88/100
   - matches your favorite genre (pop)
   - matches your favorite mood (happy)
   - energy (0.82) is close to what you want (0.8)
   - has the non-acoustic energy you tend to like

2. Gym Hero (Max Pulse) - Score: 62/100
   - matches your favorite genre (pop)
   - energy (0.93) is close to what you want (0.8)
   - has the non-acoustic energy you tend to like

3. Rooftop Lights (Indigo Parade) - Score: 51/100
   - matches your favorite mood (happy)
   - energy (0.76) is close to what you want (0.8)

4. Recess (Bubblegum Static) - Score: 29/100
   - energy (0.8) is close to what you want (0.8)
   - has the non-acoustic energy you tend to like

5. Warehouse 88 (Kilo Frame) - Score: 28/100
   - energy (0.88) is close to what you want (0.8)
   - has the non-acoustic energy you tend to like
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



