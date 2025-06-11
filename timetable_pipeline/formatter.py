import pandas as pd

# 🔧 Shared builder (with corrected fields)
def build_row(row, idx):
    return {
        "ID": idx + 1,
        "SectionID": row.get("SectionID"),
        "SlotIndex": row.get("SlotIndex"),
        "SubjectCode": row.get("SubjectCode"),
        "TeacherID": row.get("TeacherID"),
        "Scheme": row.get("Scheme"),
        "Subject": row.get("Subject"),
        "RoomType": row.get("RoomType"),
        "Block": row.get("Block"),
        "Day": int(row.get("SlotIndex", 0)) // 8,
        "StartHour": 8 + (int(row.get("SlotIndex", 0)) % 8),
        "EndHour": 9 + (int(row.get("SlotIndex", 0)) % 8),
        "Type": "Lab" if str(row.get("RoomType")).lower() == "lab" else "Theory"
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

# 🔀 Wrapper for Streamlit
def format_output(df: pd.DataFrame, mode: str = "admin") -> pd.DataFrame:
    if mode == "section":
        return format_section_view(df)
    elif mode == "teacher":
        return format_teacher_view(df)
    else:
        return format_admin_view(df)
