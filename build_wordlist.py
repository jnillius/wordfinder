# annotate_wordlist.py
import csv
import nltk
from nltk.corpus import wordnet as wn
from collections import defaultdict
import sys

nltk.download('wordnet')

# Optional: enable spaCy fallback if you installed it
USE_SPACY = True
try:
    if USE_SPACY:
        import spacy
        nlp = spacy.load("en_core_web_sm")
except Exception:
    USE_SPACY = False

pos_map = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}

def get_poses_for_lemma(lemma):
    """Return set of readable POS tags + first definition for a lemma using WordNet."""
    synsets = wn.synsets(lemma)
    poses = set()
    definition = ""
    if synsets:
        for s in synsets:
            poses.add(pos_map.get(s.pos(), s.pos()))
        definition = synsets[0].definition()
    return poses, definition

def main(words_file="words_alpha.txt", out_csv="words_with_pos.csv"):
    # Load words (one per line)
    with open(words_file, encoding="utf-8") as f:
        all_words = [w.strip().lower() for w in f if w.strip()]

    # Cache for lemma -> (poses_set, definition)
    lemma_cache = {}

    rows_written = 0
    with open(out_csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["word", "pos", "lemma", "definition"])

        for i, word in enumerate(all_words, start=1):
            if i % 10000 == 0:
                print(f"Processed {i} words...", file=sys.stderr)

            # Try WordNet directly
            synsets = wn.synsets(word)
            poses = set()
            definition = ""

            if synsets:
                for s in synsets:
                    poses.add(pos_map.get(s.pos(), s.pos()))
                definition = synsets[0].definition()
                lemma = word  # already a lemma in WordNet
            else:
                # Try morphological normalization (e.g. "starts" -> "start")
                lemma = wn.morphy(word)
                if lemma:
                    if lemma in lemma_cache:
                        poses, definition = lemma_cache[lemma]
                    else:
                        poses, definition = get_poses_for_lemma(lemma)
                        lemma_cache[lemma] = (poses, definition)

            # Fallback to spaCy single-token POS if WordNet provided nothing
            if not poses and USE_SPACY:
                try:
                    doc = nlp(word)
                    tok = doc[0]
                    # spaCy returns UPOS like NOUN/VERB/ADJ/ADV
                    spacy_pos = tok.pos_.lower()
                    # Map spaCy to similar words used above (quick mapping)
                    spacy_map = {'noun':'noun','verb':'verb','adj':'adjective','adv':'adverb','x':'unknown'}
                    mapped = spacy_map.get(spacy_pos, spacy_pos)
                    poses = {mapped}
                    definition = ""  # spaCy doesn't provide definition
                except Exception:
                    poses = set()

            # If still nothing, mark unknown
            if not poses:
                poses = {"unknown"}
                definition = ""

            # Write one row per pos (gives easy filtering later)
            for p in sorted(poses):
                writer.writerow([word, p, lemma or "", definition or ""])
                rows_written += 1

    print(f"Done — wrote {rows_written} rows to {out_csv}")

if __name__ == "__main__":
    main()
