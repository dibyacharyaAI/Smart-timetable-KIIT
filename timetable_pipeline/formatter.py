import pandas as pd

# 🔧 Human-readable builder
def build_row(row, idx):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    slot = int(row.get("SlotIndex", 0))
    day = day_names[slot // 8] if slot // 8 < len(day_names) else "Unknown"
    start = 8 + (slot % 8)
    end = start + 1
    time = f"{start}:00 - {end}:00"

    return {
        "ID": idx + 1,
        "Section": row.get("SectionID"),
        "Day": day,
        "Time": time,
        "SubjectCode": row.get("SubjectCode"),
        "Subject": row.get("Subject"),
        "TeacherID": row.get("TeacherID"),
        "TeacherName": row.get("TeacherName", "Unknown"),
        "Scheme": row.get("Scheme"),
        "RoomType": row.get("RoomType"),
        "Block": row.get("Block"),
        "Type": "Lab" if str(row.get("RoomType")).strip().lower() == "lab" else "Theory"
    }

# 📋 Admin full view
def format_admin_view(df: pd.DataFrame) -> pd.DataFrame:
    data = [build_row(row, i) for i, row in df.iterrows()]
    return pd.DataFrame(data)

# 📋 Section-wise view
def format_section_view(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    for sid in df["SectionID"].unique():
        filtered = df[df["SectionID"] == sid]
        result.extend([build_row(row, i) for i, row in filtered.iterrows()])
    return pd.DataFrame(result)

# 📋 Teacher-wise view
def format_teacher_view(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    for tid in df["TeacherID"].astype(str).unique():
        filtered = df[df["TeacherID"].astype(str) == str(tid)]
        result.extend([build_row(row, i) for i, row in filtered.iterrows()])
    return pd.DataFrame(result)

# 🔁 Final output dispatcher
def format_output(df: pd.DataFrame, mode: str = "admin") -> pd.DataFrame:
    if mode == "section":
        return format_section_view(df)
    elif mode == "teacher":
        return format_teacher_view(df)
    else:
        return format_admin_view(df)
