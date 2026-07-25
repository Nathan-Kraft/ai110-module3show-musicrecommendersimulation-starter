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

Real-world music recommenders (Spotify, Apple Music, etc.) typically blend two approaches: content-based filtering, which matches a song's own attributes (genre, tempo, mood, acoustic qualities) against a listener's stated or inferred tastes, and collaborative filtering, which looks at what similar users listened to and recommends based on those patterns, even without knowing why a song fits. Production systems also weigh signals we're not using here, like skip rates, replay counts, time of day, and social trends, and they constantly re-rank based on real-time feedback rather than a single static formula. Once candidate songs are scored, real-world systems rank and re-rank them using additional business logic (diversity, freshness, promotion) before final selection, a separate step from computing the raw score.

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
  - **Observed example**: in the Diverse Profiles Tests above, "Storm Runner" lands in 1st place for several very different profiles (Taste Profile, Conflicted Energy/Mood Edge Case, and near the top for others). This isn't a weighting bug: Storm Runner happens to be one of only two "rock" songs and holds the catalog's highest energy (0.91) and tempo (152 bpm). Any profile wanting high energy, fast tempo, or an "intense" vibe scores it well on `energy_closeness`/`tempo_closeness` alone, and it also picks up genre/mood match bonuses for rock/intense seekers, letting it stack nearly every weighted term at once. With only one song sitting at that extreme, there's no competing track nearby to challenge it. A larger, more evenly distributed catalog would likely reduce this effect.
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

## Diverse Profiles Tests

Ran the `Recommender` (OOP) class against six sample `UserProfile`s defined in `main.py`, including two deliberate edge cases where a user's stated preferences pull the scoring in different directions.

### Taste Profile (genre=rock, mood=intense, energy=0.65, tempo=140, likes_acoustic=False)

```
1. Storm Runner (Voltline) - Score: 93/100
   - matches your favorite genre (rock)
   - matches your favorite mood (intense)
   - tempo (152.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

2. Gym Hero (Max Pulse) - Score: 58/100
   - matches your favorite mood (intense)
   - tempo (132.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

3. Habana Nights (Sol y Sombra) - Score: 34/100
   - energy (0.68) is close to what you want (0.65)
   - has the non-acoustic energy you tend to like

4. Night Drive Loop (Neon Echo) - Score: 34/100
   - energy (0.75) is close to what you want (0.65)
   - has the non-acoustic energy you tend to like

5. Warehouse 88 (Kilo Frame) - Score: 34/100
   - tempo (126.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like
```

### High-Energy Pop Fan (genre=High-Energy Pop, mood=euphoric, energy=0.9, tempo=128, likes_acoustic=False)

```
1. Warehouse 88 (Kilo Frame) - Score: 64/100
   - matches your favorite mood (euphoric)
   - energy (0.88) is close to what you want (0.9)
   - tempo (126.0 bpm) is close to what you want (128 bpm)
   - has the non-acoustic energy you tend to like

2. Gym Hero (Max Pulse) - Score: 39/100
   - energy (0.93) is close to what you want (0.9)
   - tempo (132.0 bpm) is close to what you want (128 bpm)
   - has the non-acoustic energy you tend to like

3. Storm Runner (Voltline) - Score: 37/100
   - energy (0.91) is close to what you want (0.9)
   - tempo (152.0 bpm) is close to what you want (128 bpm)
   - has the non-acoustic energy you tend to like

4. Sunrise City (Neon Echo) - Score: 36/100
   - energy (0.82) is close to what you want (0.9)
   - tempo (118.0 bpm) is close to what you want (128 bpm)
   - has the non-acoustic energy you tend to like

5. Fever Dream (Static Cathedral) - Score: 36/100
   - energy (0.97) is close to what you want (0.9)
   - has the non-acoustic energy you tend to like
```

### Chill Lofi Fan (genre=Chill Lofi, mood=relaxed, energy=0.25, tempo=75, likes_acoustic=True)

```
1. Coffee Shop Stories (Slow Stereo) - Score: 61/100
   - matches your favorite mood (relaxed)
   - energy (0.37) is close to what you want (0.25)
   - tempo (90.0 bpm) is close to what you want (75 bpm)
   - has an acoustic feel you tend to like

2. Glass Cathedral (Aria Ninwe) - Score: 38/100
   - energy (0.25) is close to what you want (0.25)
   - tempo (58.0 bpm) is close to what you want (75 bpm)
   - has an acoustic feel you tend to like

3. Spacewalk Thoughts (Orbit Bloom) - Score: 38/100
   - energy (0.28) is close to what you want (0.25)
   - tempo (60.0 bpm) is close to what you want (75 bpm)
   - has an acoustic feel you tend to like

4. Rust Belt Ghosts (Hollow Creek) - Score: 37/100
   - energy (0.3) is close to what you want (0.25)
   - tempo (68.0 bpm) is close to what you want (75 bpm)
   - has an acoustic feel you tend to like

5. Library Rain (Paper Lanterns) - Score: 36/100
   - energy (0.35) is close to what you want (0.25)
   - tempo (72.0 bpm) is close to what you want (75 bpm)
   - has an acoustic feel you tend to like
```

### Deep Intense Rock Fan (genre=Deep Intense Rock, mood=intense, energy=0.8, tempo=140, likes_acoustic=False)

```
1. Gym Hero (Max Pulse) - Score: 61/100
   - matches your favorite mood (intense)
   - energy (0.93) is close to what you want (0.8)
   - tempo (132.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

2. Storm Runner (Voltline) - Score: 61/100
   - matches your favorite mood (intense)
   - energy (0.91) is close to what you want (0.8)
   - tempo (152.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

3. Warehouse 88 (Kilo Frame) - Score: 37/100
   - energy (0.88) is close to what you want (0.8)
   - tempo (126.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

4. Sunrise City (Neon Echo) - Score: 36/100
   - energy (0.82) is close to what you want (0.8)
   - tempo (118.0 bpm) is close to what you want (140 bpm)
   - has the non-acoustic energy you tend to like

5. Recess (Bubblegum Static) - Score: 36/100
   - energy (0.8) is close to what you want (0.8)
   - has the non-acoustic energy you tend to like
```

### Conflicted Energy/Mood Edge Case (genre=rock, mood=sad, energy=0.95, tempo=170, likes_acoustic=True)

```
1. Storm Runner (Voltline) - Score: 64/100
   - matches your favorite genre (rock)
   - energy (0.91) is close to what you want (0.95)
   - tempo (152.0 bpm) is close to what you want (170 bpm)

2. Broken Halo (Marlowe Vance) - Score: 43/100
   - matches your favorite mood (sad)
   - has an acoustic feel you tend to like

3. Riot Gear (Vex Culprit) - Score: 30/100
   - energy (0.95) is close to what you want (0.95)
   - tempo (175.0 bpm) is close to what you want (170 bpm)

4. Fever Dream (Static Cathedral) - Score: 30/100
   - energy (0.97) is close to what you want (0.95)
   - tempo (168.0 bpm) is close to what you want (170 bpm)

5. Gym Hero (Max Pulse) - Score: 28/100
   - energy (0.93) is close to what you want (0.95)
```

### Mismatched Genre Expectations Edge Case (genre=classical, mood=euphoric, energy=0.9, tempo=60, likes_acoustic=False)

```
1. Warehouse 88 (Kilo Frame) - Score: 60/100
   - matches your favorite mood (euphoric)
   - energy (0.88) is close to what you want (0.9)
   - has the non-acoustic energy you tend to like

2. Glass Cathedral (Aria Ninwe) - Score: 52/100
   - matches your favorite genre (classical)
   - tempo (58.0 bpm) is close to what you want (60 bpm)

3. Recess (Bubblegum Static) - Score: 35/100
   - energy (0.8) is close to what you want (0.9)
   - has the non-acoustic energy you tend to like

4. Gym Hero (Max Pulse) - Score: 34/100
   - energy (0.93) is close to what you want (0.9)
   - has the non-acoustic energy you tend to like

5. Storm Runner (Voltline) - Score: 33/100
   - energy (0.91) is close to what you want (0.9)
   - has the non-acoustic energy you tend to like
```

---

## Experiments You Tried

Ideas for future experiments:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

### Disabling the mood check

We temporarily commented out the mood-matching logic in both scoring implementations (`Recommender._score()` and `score_song()` in `src/recommender.py`), then re-ran the test suite and `src/main.py` against all six sample profiles to see how rankings changed with `MOOD_WEIGHT` (0.25) effectively removed from every song's score.

**What happened:**

- **Rankings mostly held steady at #1** for profiles where genre/energy/tempo already dominated the top pick (Taste Profile, Conflicted Energy/Mood Edge Case, Mismatched Genre Expectations Edge Case). Mood wasn't the deciding factor for those top spots, so removing it didn't reshuffle the winner.
- **Scores compressed at the top.** Songs that previously separated themselves with a mood match bonus (Storm Runner's 93/100 dropped to 68/100 on the Taste Profile; Warehouse 88's 64/100 dropped to 39/100 on the High-Energy Pop Fan profile) fell by roughly the full 25-point mood bonus, closing the gap to the runner-up.
- **Lower ranks clustered even tighter.** With one fewer either/or bonus in play, songs 2 through 5 in several profiles landed within 1-2 points of each other (Deep Intense Rock Fan: ranks 1-5 spanning only 36-37/100), making the tail of the ranking feel almost arbitrary.
- **The displayed "/100" score became misleading.** `main.py` still multiplies the raw score by 100 without adjusting for the missing weight, so the real achievable ceiling dropped to 75/100 (or 65/100 for profiles with no `target_tempo`), even though the label still implies a 0-100 scale.
- **Tests still passed (2/2).** `tests/test_recommender.py` doesn't assert on mood specifically, so removing it didn't break any existing test. That's a reminder that passing tests confirm the code runs, not that the recommendations are still meaningful.

**Takeaway:** this change made the recommendations different, not more accurate. There's no ground-truth labeled dataset to validate recommendation quality against; the system's "correctness" is defined by the weights we deliberately chose. Dropping mood just silently removes one of five stated user preferences from consideration rather than fixing an error. This was most visible in the Conflicted Energy/Mood Edge Case profile, which was specifically built so mood and energy/tempo pull in opposite directions. Disabling mood erases that intentional tension by construction. We restored the mood check afterward and confirmed the tests still passed unchanged.

---

## Limitations and Risks

- **Tiny, unevenly distributed catalog**: only 20 songs across 17 genres and 16 moods, so most genre/mood values have just one matching song. A user's "genre match" is usually a bet on a single track rather than a real cluster of options (see the Storm Runner example above).
- **All-or-nothing genre/mood matching**: genre and mood use exact string matching with no partial credit for adjacent styles (e.g., "pop" gets zero credit from an "indie pop" or "synthwave" song, even though they're stylistically close). Since these two terms make up 60% of the score, this brittleness has an outsized effect on rankings.
- **No understanding of the music itself**: the system only reasons about structured metadata (genre, mood, energy, tempo, acousticness). It has no awareness of lyrics, language, vocals vs. instrumental, or era, so it can't distinguish songs on any dimension outside those five fields.
- **No memory or feedback loop**: each recommendation is computed fresh from a static profile. The system doesn't learn from what a user actually plays, skips, or rates, so it will recommend the same top songs to the same profile forever, and can't adapt over time the way collaborative filtering does.
- **No diversity control**: recommendations are pure score-ranked with no per-artist or per-genre cap, so a top-5 list can end up dominated by one or two songs/artists that happen to score well, rather than offering a varied set.
- **Fairness risk**: users whose taste aligns with a well-represented genre/mood get many strong, well-differentiated matches, while users with niche, blended, or descriptively-phrased tastes (e.g., "High-Energy Pop" instead of "pop") get weaker, less discriminating results, purely as an artifact of catalog coverage and string matching, not their taste being less valid.

See `model_card.md` for a deeper analysis, including specific evaluation runs that surfaced several of these limitations in practice.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)
