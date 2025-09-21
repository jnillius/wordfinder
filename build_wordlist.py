import csv
import spacy
import nltk
from nltk.corpus import wordnet as wn
import sys

nltk.download("wordnet")

print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
print("Model loaded.")

# Mapping from WordNet POS tags to the simplified tags used in the app
pos_map = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "r": "adverb",
    "s": "adjective",  # Adjective satellite
}

# Mapping from spaCy's detailed POS tags to a consistent, readable format
spacy_pos_map = {
    "adj": "adjective",
    "adp": "adposition",
    "adv": "adverb",
    "aux": "auxiliary",
    "cconj": "conjunction",
    "det": "determiner",
    "intj": "interjection",
    "noun": "noun",
    "num": "numeral",
    "part": "particle",
    "pron": "pronoun",
    "propn": "proper noun",
    "punct": "punctuation",
    "sconj": "conjunction",
    "verb": "verb",
    "x": "unknown",
}


def main(words_file="words_alpha.txt", out_csv="words_data.csv"):
    # Load words (one per line)
    with open(words_file, encoding="utf-8") as f:
        all_words = [w.strip().lower() for w in f if w.strip()]

    rows_written = 0
    pos_from_wordnet_count = 0
    pos_from_spacy_count = 0
    pos_unknown_count = 0
    with open(out_csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)

        # Process words in batches for better performance
        for i in range(0, len(all_words), 10000):
            batch = all_words[i : i + 10000]

            # Use nlp.pipe for efficient fallback processing if needed
            docs = nlp.pipe(batch)
            docs_iterator = iter(docs)

            for word in batch:
                # ALWAYS get the next doc from the iterator to keep it in sync with the word loop
                try:
                    doc = next(docs_iterator)
                except StopIteration:
                    doc = None  # Safeguard, should not happen

                poses = set()
                definition = ""

                # 1. Get all POS tags and a definition from WordNet
                synsets = wn.synsets(word)
                if synsets:
                    for s in synsets:
                        # Use the mapping to get simplified POS tags
                        poses.add(pos_map.get(s.pos(), s.pos()))
                        pos_from_wordnet_count += 1
                    definition = synsets[0].definition()

                # 2. Fallback to spaCy if WordNet found nothing
                if not poses:
                    try:
                        # The nlp.pipe iterator is advanced here for each word
                        if doc and doc[0]:
                            # Use spaCy's detailed POS tag, mapped to our format
                            spacy_pos = doc[0].pos_.lower()
                            poses = {spacy_pos_map.get(spacy_pos, "unknown")}
                            pos_from_spacy_count += 1
                    except Exception:
                        poses = {"unknown"}

                # If still nothing, mark as unknown
                if not poses:
                    poses = {"unknown"}
                    pos_unknown_count += 1

                # Write one row for each part of speech found
                for p in sorted(list(poses)):
                    writer.writerow([word, p, definition])
                    rows_written += 1

            print(f"Processed {i + len(batch)} of {len(all_words)} words...", file=sys.stderr)

    print(
        f"Found {pos_from_wordnet_count} POS tags from WordNet, {pos_from_spacy_count} from spaCy, {pos_unknown_count} unknown",
        file=sys.stderr,
    )
    print(f"Done — wrote {rows_written} rows to {out_csv}")


if __name__ == "__main__":
    main()
