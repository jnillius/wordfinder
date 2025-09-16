from flask import Flask, request, render_template

app = Flask(__name__)

# Load word list
with open("words.txt") as f:
    words = [w.strip().lower() for w in f.readlines()]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        length = int(request.form.get("length"))
        start = request.form.get("start").lower()
        end = request.form.get("end").lower()

        # Filtering words
        results = [w for w in words if len(w) == length and w.startswith(start) and w.endswith(end)]

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run()