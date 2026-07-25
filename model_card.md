# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  
**VibeMatch**


---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

**VibeMatch is a content-based recommendation demo** that ranks a fixed 20-song catalog against a single stated `UserProfile` (favorite genre, favorite mood, target energy, optional target tempo, and an acoustic preference), returning the top-k songs with a plain-language explanation for each pick.

It generates **ranked "you might like this" lists**, not predictions of what a person will actually play next: it has no listening history, skip data, or feedback loop, so it can only reason about stated preferences, never inferred or observed ones.

It assumes the user **can and does articulate their taste precisely**: genre and mood have to be typed as exact strings matching the catalog's vocabulary (e.g., "pop," "intense"), and a close phrasing like "High-Energy Pop" gets zero credit rather than partial credit. It also assumes a single static profile per user, with no support for taste changing by time of day, mood swings, or multiple listening contexts.

This is a **classroom exploration project**, not a production recommender: the catalog is small (20 songs), there's no real user base, and its purpose is to make the scoring logic fully transparent and inspectable so its strengths and biases (see Sections 5–6) can be reasoned about directly, rather than to serve real listeners.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

**Every song in the catalog carries a handful of tags and numbers**: a genre (like "pop" or "rock"), a mood (like "happy" or "intense"), and three 0-to-1 style dials, energy, danceability, and acousticness, plus a tempo in beats per minute. A listener's taste profile mirrors most of this: a favorite genre, a favorite mood, a target energy level, an optional target tempo, and whether they lean toward acoustic or non-acoustic sound.

To score a song for a listener, the model hands out points in five buckets and adds them up:

- **35 points (out of 100)** if the song's genre exactly matches the listener's favorite genre
- **25 points** if the song's mood exactly matches the listener's favorite mood
- **20 points** based on how close the song's energy is to the listener's target energy, full credit for an exact match, shrinking the further apart they are
- **10 points** the same way, but for tempo, only if the listener stated a tempo preference
- **10 points** for how well the song's acoustic-ness lines up with whether the listener said they like acoustic or non-acoustic sound

Those five numbers are added together into a single score out of 100, and the catalog is sorted from highest to lowest. The top few songs are handed back to the listener, each with a short written reason (like "matches your favorite genre" or "energy is close to what you want") built from whichever buckets actually scored points, so every recommendation can be explained rather than being a black box.

Two of the song catalog's numbers, valence and danceability, are tracked in the data but never used in scoring. That was a deliberate simplicity choice: adding more dials would mean more to explain, so this version sticks to the five buckets above rather than folding every available number into the score.

The genre and mood checks are strict, all-or-nothing string matches. There's no partial credit for genres that feel similar to a person (like "pop" and "indie pop"), which is a deliberate simplicity trade-off discussed more in Sections 6 and 7. No changes were made to the starter's weighting or formula; the scoring logic here reflects the original 35/25/20/10/10 recipe.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

**The catalog is the 20-song CSV in `data/songs.csv`**, unchanged from the starter project, no rows were added or removed. Each song carries an id, title, artist, genre, mood, and five numeric traits: energy, tempo (bpm), valence, danceability, and acousticness.

**Genres represented (17 across 20 songs)**: pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, metal, latin, blues, house, country, hip hop, classical, punk, and dream pop. Most genres appear only once or twice, so there's very little internal variety within any single genre (see the "Storm Runner" example in Section 6, where a genre having just one strong candidate lets that song dominate multiple unrelated user profiles).

**Moods represented (16 across 20 songs)**: happy, chill, intense, relaxed, moody, focused, melancholic, angry, romantic, sad, euphoric, nostalgic, playful, peaceful, rebellious, and dreamy, again mostly one song per mood, so a listener's mood match is usually an all-or-nothing bet on a single track rather than a real cluster of options.

**What's missing from this dataset**: there's no vocal/instrumental flag, no language or lyrical content, no artist popularity or era/decade info, and no way to tag a song with more than one genre even when it clearly blends styles (e.g., "dream pop" and "synthwave" share real sonic overlap but are scored as unrelated categories). There's also no notion of a listener's broader context, like time of day, activity, or social setting, that real recommenders often use alongside song attributes. With only 20 songs and 1–2 per genre/mood pairing, the catalog is far too small and unevenly distributed to represent the actual diversity of musical taste; it's meant to be illustrative for this classroom project, not representative of a real listening library.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

**The system works best for listeners whose profile vocabulary lines up exactly with the catalog's labels.** The starter "genre=pop, mood=happy, energy=0.8" demo and the "Taste Profile" (rock/intense/tempo=140) and "Chill Lofi Fan" (relaxed/acoustic/low-energy/low-tempo) cases from Section 7 all produce a clear, sensible top pick whose reasons line up with intuition: Sunrise City for the happy pop fan, Storm Runner for the rock/intense fan, Coffee Shop Stories for the chill acoustic fan. In each of these, the top song wins by a wide margin, not a tie or a coin-flip, which suggests the scoring is doing real discriminating work when genre and mood are stated in the catalog's own vocabulary.

**Numeric closeness (energy, tempo, acousticness) behaves the way you'd want it to.** Across every profile tested, songs whose energy or tempo sit near the target reliably rank higher than songs further away, and the acoustic/non-acoustic split correctly separates songs like Glass Cathedral (acoustic) from Fever Dream (non-acoustic). This part of the scoring generalizes well even for profiles with no exact genre/mood match, since it doesn't depend on string spelling the way genre/mood matching does.

**Every recommendation is explainable, not just ranked.** Because the score is a transparent sum of named components, the system can always say *why* a song was picked, "matches your favorite genre," "energy is close to what you want," rather than handing back an opaque number. That auditability is a genuine strength for a classroom tool meant to teach how content-based recommenders reason, even in the edge cases where the ranking itself feels off (Section 6), you can always point to exactly which term caused it.

**It behaves predictably and deterministically.** The same profile against the same catalog always produces the same ranked list (ties are broken by song id), so behavior is easy to reason about, debug, and explain to someone learning how the system works, unlike collaborative-filtering systems whose behavior can shift based on other users' data.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

During testing we found that the genre and mood matching is all-or-nothing: a song either exactly matches the user's stated `favorite_genre`/`favorite_mood` or it gets no credit at all, even when it is musically close (for example, a "pop" fan gets no boost from an "indie pop" or "synthwave" track, despite those being adjacent styles in the catalog). Because genre and mood together make up 60% of the score, and the user profile never updates based on what they listen to, the recommender tends to keep resurfacing the same narrow slice of the catalog rather than branching out, producing a filter-bubble effect. This was compounded by the lack of any per-artist diversity check, so a user's top-5 list could end up dominated by just one or two artists who happen to share their favorite genre. We'd consider this a fairness issue as much as a quality one: users whose taste happens to align with a well-represented genre in the data get many strong matches, while users with niche or blended tastes get comparatively rushed, exact-match-or-nothing scores.

**Update:** the per-artist crowding half of this problem now has a mitigation, the `artist_penalty` re-ranking described in Section 8. It targets fairness on two levels. First, listener fairness: without it, a listener whose taste happens to line up with one prolific, well-represented artist gets a top-5 that is really just five variations on one artist's sound, while a listener with more scattered taste already got a naturally varied list, so the "quality" of the experience quietly depended on how the catalog happened to be distributed rather than on how well the system understood either listener. Spreading picks across artists closes that gap. Second, catalog/artist-side fairness: a plain highest-score sort always reads back whichever artist happens to have the most tracks clustered near a popular preference (see the "Storm Runner" pattern in Section 4 and Section 7), so that artist's exposure compounds across many similar profiles purely from having more shots on goal, not from being a better match. Penalizing repeats gives lower-scoring artists a real chance to surface instead of being permanently crowded out. The mitigation is opt-in and off by default (`artist_penalty=0`), so a caller who never sets it still sees the plain-score behavior described above; it has to be deliberately turned on (via `recommend()`/`recommend_songs()`, or the y/N prompt in `main.py`) for either fairness benefit to take effect.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

We ran the sample profiles defined in `src/main.py` against the full 20-song catalog: a straightforward rock/intense taste profile, a conflicted-preferences edge case (wants a fast, high-energy rock song but says the mood should be "sad" and that they like acoustic textures), and a mismatched-genre edge case (picks "classical" but wants a euphoric, high-energy, non-acoustic, slow-tempo song). We also tried three profiles that named more descriptive genre labels, "High-Energy Pop," "Chill Lofi," and "Deep Intense Rock," to see how the system handled phrasing that felt natural to a user but didn't exactly match a genre string in the catalog.

The biggest surprise was that those three descriptive-label profiles never matched on genre at all, since the CSV only stores plain labels like "pop," "lofi," and "rock," so `GENRE_WEIGHT` (0.35 of the score) sat unused for every song and rankings were driven entirely by mood, energy, tempo, and acousticness. We hadn't expected genre matching to be so brittle to phrasing. The conflicted-preferences profile was also revealing: the top-ranked song (a genre and energy match) beat out the one song that actually matched the stated mood and acoustic preference, confirming that genre match alone can outweigh two other matched features combined. In the mismatched-genre case, the exact genre match ("classical") still lost to a song with no genre match at all, because that song picked up mood, energy, and acoustic points instead, showing that a single strong categorical match doesn't guarantee the top spot the way we initially assumed.

### Comparing profiles side by side

*Functional "Happy Pop" (genre=pop, mood=happy, energy=0.8) vs. "High-Energy Pop Fan" (genre="High-Energy Pop", mood=euphoric, energy=0.9).* Both listeners think of themselves as pop fans, but they get completely different top picks. The "Happy Pop" listener gets Sunrise City up top because it matches the genre word "pop" and the mood word "happy." The "High-Energy Pop Fan," despite wanting basically the same kind of music, never gets that genre credit at all, because the system only checks if the words are an exact match, and "High-Energy Pop" isn't spelled the same as "pop." So their top pick (Warehouse 88) is chosen almost entirely on energy and tempo instead. Two people with very similar taste end up with different recommendations for a reason that has nothing to do with their taste: it's just about how they happened to type the genre name.

This is also exactly why **Gym Hero keeps showing up for the "Happy Pop" listener**, even though its mood is "intense," not "happy." Gym Hero still checks two other boxes: it's genre "pop," and its energy (0.93) is close to what the listener asked for (0.8), and those two checks alone are worth more than half the total score. The system never asks "does this song actually feel happy," it just adds up points for each box that's checked, so a loud, intense pop song can out-earn a song that's a worse genre/energy fit but a true mood match. In plain terms: the system is scoring "does this tick enough boxes," not "does this feel like what the person wants," so a technically-high-scoring song can still miss the vibe.

*Taste Profile (genre=rock, mood=intense, energy=0.65) vs. "Deep Intense Rock Fan" (genre="Deep Intense Rock", mood=intense, energy=0.8).* Both want the same kind of music (loud, intense rock), but only the first one spelled the genre in a way the system recognizes. Storm Runner wins clearly for the Taste Profile listener because it gets full credit for matching "rock." For the Deep Intense Rock Fan, Storm Runner ties in score with Gym Hero, since "Deep Intense Rock" never matches anything, and Storm Runner only wins the tie because of its lower catalog ID — not because it's actually the better match. So one rock fan gets a confident, well-earned top pick, and an almost-identical rock fan gets the same song by what's essentially a coin flip.

*Chill Lofi Fan (energy=0.25, tempo=75, likes_acoustic=True) vs. Conflicted Energy/Mood Edge Case (energy=0.95, tempo=170, mood="sad", likes_acoustic=True).* The Chill Lofi Fan's top pick, Coffee Shop Stories, makes sense end to end: it's slow, soft, and acoustic, matching everything they asked for. The Conflicted profile asked for something almost the opposite of chill on paper (very high energy, very fast tempo) while also saying they want a "sad" mood and an acoustic feel — a contradiction. The system's top pick, Storm Runner, is loud, fast rock that completely ignores the "sad" and "acoustic" parts of the request. That happens because genre + energy + tempo together are worth 65% of the score, while mood + acoustic are only worth 35%, so when a listener's stated wants pull in two directions, the system just sides with whichever half carries more weight, even if that means ignoring half of what the person said they wanted.

*Mismatched Genre Expectations Edge Case (genre="classical," mood="euphoric," energy=0.9, tempo=60) vs. Conflicted Energy/Mood Edge Case.* Both profiles are deliberately contradictory, but the system resolves them differently, which shows how fragile a single strong match can be. In the classical case, the one song that matches the genre exactly (Glass Cathedral) is slow and low-energy, which clashes with the "euphoric, high-energy" part of the request, so it loses enough points elsewhere that it drops to second place behind a song with no genre match at all. In the conflicted-rock case, the genre-matching song (Storm Runner) happens to still be close on energy and tempo, so it wins outright even while ignoring mood and acoustic preference entirely. The takeaway: matching someone's favorite genre only helps if the rest of the song also lines up with what they asked for — it's not a guaranteed win on its own.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

**Fuzzy/synonym-aware genre and mood matching.** The evaluation in Section 7 showed that "High-Energy Pop" and "Deep Intense Rock" get zero genre credit against "pop" and "rock" even though they describe the same taste, and even catalog-adjacent styles like "indie pop" vs. "pop" score as total mismatches. A synonym map or similarity check would let close-but-not-identical phrasing earn partial credit instead of losing 35 points outright, fixing the single biggest surprise from testing.

**A diversity/anti-repetition pass over the top-k results.** ~~Section 6 noted that a user's top-5 can end up dominated by one or two artists or one genre, since nothing currently penalizes redundancy. Re-ranking to cap results per artist, or explicitly rewarding variety, would directly address the filter-bubble/fairness concern raised there.~~ **Implemented:** `recommend()` and `recommend_songs()` now take an `artist_penalty` parameter (default `0`, off). When set above zero, top-k selection becomes greedy instead of a single sort: after each pick, `artist_penalty` is subtracted from the remaining score of every other song by that same artist, before the next pick is chosen. So the first pick is always still the single best-scoring song, but from the second pick on, an artist who already has a song in the list has to clear a higher bar to get a second one in, which gives other, lower-scoring artists room to surface instead of being crowded out. It is opt-in (`artist_penalty=0` reproduces the old plain-score ranking exactly) and is now surfaced as a y/N prompt in `main.py` ("Penalize repeat artists to encourage variety?") alongside the existing strategy prompt, so both the functional and OOP demo runs can be compared with and without it. Genre-level diversity (as opposed to artist-level) is not yet addressed and would need a similar per-genre penalty.

**Bring `valence` and `danceability` into the score.** Both are already tracked per song but unused (Sections 3–4). Adding `target_valence` and `likes_danceable` fields to `UserProfile` would use more of the available signal and help distinguish songs that currently tie on every scored dimension.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

**My biggest learning moment** was watching exact-string genre matching break for names that felt completely reasonable to type, like "High-Energy Pop" or "Deep Intense Rock." Building this project made the mechanics of a recommender feel a lot less mysterious to me, and a lot more like arithmetic wearing a friendly interface: every "personalized" pick was really just a weighted sum of exact-match checks and distance calculations, dressed up with a plain-language explanation. I found that oddly reassuring and a little unsettling at the same time. Reassuring because I could always point to the exact term that produced a score, but unsettling because it meant I could build a system that looked confident and personalized while actually being driven by something as shallow as whether I'd typed a genre string one way instead of another.

When I watched two nearly identical rock fans get wildly different-quality recommendations, one confident, one basically a coin-flip tie, it became obvious to me how much a system's "understanding" of a user can hinge on brittle string comparisons rather than any real grasp of taste. It also reframed how I think about bias: I'd assumed unfairness in recommenders mainly came from bad or skewed training data, but building this showed me it can just as easily come from rigid scoring rules that quietly reward users lucky enough to phrase things the way the system expects.

I used Claude Code to help me derive a distance-based "closeness" formula for numeric features like energy and tempo, then chose weights (genre 0.35, mood 0.25, energy 0.20, tempo 0.10, acoustic 0.10) based on a specific tiebreaker scenario, and settled on a 0–1 internal score displayed as a score out of 100. From there, I implemented both a functional API (`load_songs`, `score_song`, `recommend_songs`) and an OOP `Recommender` class using the same algorithm, and wired them into `main.py` so it runs a full CLI simulation across six sample user profiles, including two deliberate edge cases with conflicting preferences. I also fixed a run-command bug in the README along the way. For double checking, I double check everything that the AI wants to insert before I let it. The one thing that I did need to come back to and fix was originally it wanted to implement the user profiles in the recommender.py instead of main.py. The other thing that was double checked a lot was the text paragraphs that it would use to help me answer some things in readme and here, where I would have to ask it to fix em dash useage a lot. I have tried to implement where it will do it on its own, but I stil have to figure out some kinks with that. 


**What surprised me most about simple algorithms is how convincingly they can "feel" like a recommendation** even though there's no understanding underneath. That's changed how I think about the real apps I use every day. Spotify or Apple Music's recommendations feel effortless to me, but after this project I suspect a good chunk of that "it just gets me" feeling is really about my own vocabulary and weighting lining up well with how the system happens to expect taste to be described, not some deep understanding of me as a listener.

**If I extended this project, the first thing I'd try** is fuzzy/synonym-aware genre and mood matching (see Section 8), since it directly targets the biggest weakness this reflection surfaced: a system that feels personalized but is actually one typo away from ignoring someone's real taste. I'd also want to let a real person type in their own preferences at runtime instead of only running against the predefined `UserProfile`s hardcoded in `main.py`, since every test I ran was really just me picking profiles I already expected to behave a certain way. Actual user input, even something as simple as a command-line prompt asking for genre/mood/energy, would force the system to handle phrasing and edge cases I didn't think to write into a sample profile myself.
