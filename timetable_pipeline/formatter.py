import pandas as pd

# 🔧 Human-readable row builder
def build_row(row, idx):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    try:
        slot = int(row.get("SlotIndex", 0))
    except:
        slot = 0

    day = day_names[slot // 8] if 0 <= slot // 8 < len(day_names) else "Unknown"
    start = 8 + (slot % 8)
    end = start + 1
    time = f"{start}:00 - {end}:00"

    room_type = str(row.get("RoomType", "")).strip().lower()
    class_type = "Lab" if "lab" in room_type else "Theory"

    return {
        "ID": idx + 1,
        "Section": row.get("SectionID", "NA"),
        "Day": day,
        "Time": time,
        "SubjectCode": row.get("SubjectCode", "NA"),
        "Subject": row.get("Subject", "Unknown"),
        "TeacherID": row.get("TeacherID", "NA"),
        "TeacherName": row.get("TeacherName", "Unknown Faculty"),
        "Scheme": row.get("Scheme", "NA"),
        "RoomType": row.get("RoomType", "NA"),
        "Block": row.get("Block", "Unknown-Block"),
        "Type": class_type
    }

# 📋 Admin full view
def format_admin_view(df: pd.DataFrame) -> pd.DataFrame:
    data = [build_row(row, i) for i, row in df.iterrows()]
    return pd.DataFrame(data)

# 📋 Section-wise view
def format_section_view(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    for sid in df["SectionID"].dropna().unique():
        filtered = df[df["SectionID"] == sid]
        result.extend([build_row(row, i) for i, row in filtered.iterrows()])
    return pd.DataFrame(result)

# 📋 Teacher-wise view
def format_teacher_view(df: pd.DataFrame) -> pd.DataFrame:
    result = []
    for tid in df["TeacherID"].dropna().astype(str).unique():
        filtered = df[df["TeacherID"].astype(str) == str(tid)]
        result.extend([build_row(row, i) for i, row in filtered.iterrows()])
    return pd.DataFrame(result)

# 🔁 Dispatcher
def format_output(df: pd.DataFrame, mode: str = "admin") -> pd.DataFrame:
    if mode == "section":
        return format_section_view(df)
    elif mode == "teacher":
        return format_teacher_view(df)
    else:
        return format_admin_view(df)
