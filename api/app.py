import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask, request, jsonify
import pandas as pd
from timetable_pipeline.formatter import (
    format_section_wise,
    format_teacher_wise,
    format_admin_view
)
from timetable_pipeline.process import run_full_pipeline

app = Flask(__name__)

def load_final_df():
    try:
        return pd.read_csv("data/final_transit_fixed.csv")
    except FileNotFoundError:
        return pd.DataFrame([])

@app.route("/timetable/section/<section_id>", methods=["GET"])
def get_section(section_id):
    df = load_final_df()
    section_data = df[df["SectionID"] == section_id]
    return jsonify(format_section_wise(section_data))

@app.route("/timetable/teacher/<teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    df = load_final_df()
    teacher_data = df[df["TeacherID"] == int(teacher_id)]
    return jsonify(format_teacher_wise(teacher_data))

@app.route("/timetable/admin", methods=["GET"])
def get_admin():
    df = load_final_df()
    return jsonify(format_admin_view(df))

@app.route("/upload-timetable", methods=["POST"])
def upload_and_process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    df = pd.read_csv(file)
    json_data = run_full_pipeline(df)
    return jsonify(json_data)

if __name__ == "__main__":
    app.run(debug=True)
