# timetable_pipeline/formatter.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from timetable_pipeline.formatter import format_admin_view
from timetable_pipeline.process import run_full_pipeline

import pandas as pd

def format_admin_view(df: pd.DataFrame) -> list:
    color_palette = [
        "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-100",
        "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-100",
        "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-100",
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-100",
    ]

    output = []
    for i, row in df.iterrows():
        output.append({
            "id": i + 1,
            "section": row.get("SectionID"),
            "title": row.get("Subject", "NA"),
            "day": int(row.get("SlotIndex", 0)) // 8,
            "startHour": 8 + (int(row.get("SlotIndex", 0)) % 8),
            "endHour": 9 + (int(row.get("SlotIndex", 0)) % 8),
            "type": "lab" if str(row.get("ActivityType")).lower() == "lab" else "theory",
            "room": row.get("Room", "TBD"),
            "campus": row.get("Campus", "Main"),
            "teacher": row.get("TeacherName", "Unknown"),
            "teacherId": str(row.get("TeacherID")),
            "color": color_palette[i % len(color_palette)],
        })

    return output
