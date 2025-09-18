
from flask import Flask, request, render_template
app = Flask(__name__)

# Load word list
with open("words.txt") as f:
    words = [w.strip().lower() for w in f.readlines()]

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

        # Filtering words
        results = words
        if length > 0:
            results = [w for w in results if len(w) == length]
        if start:
            results = [w for w in results if w.startswith(start)]
        if end:
            results = [w for w in results if w.endswith(end)]
        if contains:
            results = [w for w in results if contains in w]
        if contains_all:
            results = [w for w in results if all(char in w for char in contains_all)]
        if positions:
            results = [w for w in results if len(w) == len(positions) and all(positions[i] == '_' or positions[i] == w[i] for i in range(len(positions)))]

    return render_template("index.html", results=results, form_data=form_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
