# api/app.py

import sys
import os
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory

# 👇 Make sure parent folder is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from timetable_pipeline.formatter import (
    format_section_view,
    format_teacher_view,
    format_admin_view,
)
from timetable_pipeline.process import run_full_pipeline

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# 🏠 Serve frontend editor HTML
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "frontend_editor.html")

# 🔄 Load current processed timetable
def load_final_df():
    try:
        return pd.read_csv("data/final_transit_fixed.csv")
    except FileNotFoundError:
        return pd.DataFrame([])

# 📘 Section-wise API
@app.route("/timetable/section/<section_id>", methods=["GET"])
def get_section(section_id):
    df = load_final_df()
    return jsonify(format_section_view(df, section_id))

# 👨‍🏫 Teacher-wise API
@app.route("/timetable/teacher/<teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    df = load_final_df()
    return jsonify(format_teacher_view(df, teacher_id))

# 🛠️ Admin full view
@app.route("/timetable/admin", methods=["GET"])
def get_admin():
    df = load_final_df()
    return jsonify(format_admin_view(df))

# ⬆️ Upload + Process + Save CSV via Pipeline
@app.route("/upload-timetable", methods=["POST"])
def upload_and_process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    df = pd.read_csv(file)

    # ✅ Run pipeline + get processed dataframe
    final_df = run_full_pipeline(df)

    # ✅ Save as latest for all views to load
    final_df.to_csv("data/final_transit_fixed.csv", index=False)

    # ✅ Return admin-format JSON for UI
    return jsonify(format_admin_view(final_df))

from flask import send_file

@app.route("/load-final-csv")
def load_final_csv():
    try:
        return send_file("../data/final_transit_fixed.csv", mimetype="text/csv")
    except FileNotFoundError:
        return "No CSV found", 404


# 🚀 Launch API
if __name__ == "__main__":
    app.run(debug=True)
