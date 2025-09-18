
import csv
from flask import Flask, request, render_template
app = Flask(__name__)

# Load word list from CSV
words_data = []
with open("words_with_pos.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        # CSV format: word,pos,lemma,definition
        word_info = {
            "word": row[0].lower(),
            "pos": row[1],
            "definition": row[3] if len(row) > 3 else ""
        }
        words_data.append(word_info)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    form_data = {}
    if request.method == "POST":
        form_data = request.form
        length_str = request.form.get("length")
        length = int(length_str) if length_str else 0
        start = request.form.get("start", "").lower()
        end = request.form.get("end", "").lower()
        contains = request.form.get("contains", "").lower()
        contains_all = request.form.get("contains_all", "").lower()
        positions = request.form.get("positions", "").lower()
        pos_filter = request.form.get("pos")

        # Filtering words
        results = words_data
        if length > 0:
            results = [item for item in results if len(item['word']) == length]
        if start:
            results = [item for item in results if item['word'].startswith(start)]
        if end:
            results = [item for item in results if item['word'].endswith(end)]
        if contains:
            results = [item for item in results if contains in item['word']]
        if contains_all:
            results = [item for item in results if all(char in item['word'] for char in contains_all)]
        if positions:
            results = [item for item in results if len(item['word']) == len(positions) and all(positions[i] == '_' or positions[i] == item['word'][i] for i in range(len(positions)))]
        if pos_filter and pos_filter != 'any':
            results = [item for item in results if item['pos'] == pos_filter]

    return render_template("index.html", results=results, form_data=form_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
