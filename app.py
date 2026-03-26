import os
import logging
from flask import Flask, request, jsonify, send_from_directory
import spacy

# -----------------------------
# Load NLP model
# -----------------------------
nlp = spacy.load("en_core_web_sm")

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------
# Flask setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")

# -----------------------------
# Serve frontend
# -----------------------------
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok", "mode": "spacy"})

# -----------------------------
# Extraction API (NO API KEY)
# -----------------------------
@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Empty text"}), 400

    doc = nlp(text)

    nodes = []
    edges = []

    # Extract entities
    for ent in doc.ents:
        nodes.append({
            "id": ent.text,
            "label": ent.text,
            "type": ent.label_
        })

    # Extract relations (simple verb-based)
    for token in doc:
        if token.pos_ == "VERB":
            subj, obj = None, None

            for child in token.children:
                if child.dep_ in ("nsubj", "nsubjpass"):
                    subj = child.text
                if child.dep_ in ("dobj", "pobj"):
                    obj = child.text

            if subj and obj:
                edges.append({
                    "source": subj,
                    "target": obj,
                    "relation": token.text
                })

    # Remove duplicate nodes
    nodes = list({n["id"]: n for n in nodes}.values())

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    log.info("Starting server at http://127.0.0.1:5000")
    app.run(debug=True)
    print("NEW CODE RUNNING")