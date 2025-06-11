import torch
import numpy as np
import pandas as pd
from timetable_pipeline.model import load_model

def reconstruct_anomalous_sections(df, model_path, valid_tuples=None, valid_df=None, max_len=50):
    model = load_model(model_path)
    reconstructed_rows = []

    # 🔄 Normalize key string fields
    for col in ["SubjectCode", "TeacherID", "Block"]:
        df[col] = df[col].astype(str).str.strip()

    # 1️⃣ Encode categorical values
    encoded_df = df.copy()
    subject_map = {val: i for i, val in enumerate(encoded_df["SubjectCode"].unique())}
    teacher_map = {val: i for i, val in enumerate(encoded_df["TeacherID"].unique())}
    block_map = {val: i for i, val in enumerate(encoded_df["Block"].unique())}

    inv_subject_map = {v: k for k, v in subject_map.items()}
    inv_teacher_map = {v: k for k, v in teacher_map.items()}
    inv_block_map = {v: k for k, v in block_map.items()}

    encoded_df["SubjectCode"] = encoded_df["SubjectCode"].map(subject_map)
    encoded_df["TeacherID"] = encoded_df["TeacherID"].map(teacher_map)
    encoded_df["Block"] = encoded_df["Block"].map(block_map)

    # 2️⃣ Create encoded valid tuples
    valid_tuples = list(
        encoded_df[["SubjectCode", "TeacherID", "Block"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    # 🔒 Ensure valid_df is present and normalized
    if valid_df is None:
        raise ValueError("valid_df is required for contextual reconstruction.")

    for col in ["SubjectCode", "TeacherID", "Block"]:
        valid_df[col] = valid_df[col].astype(str).str.strip()

    # 3️⃣ Section-wise reconstruction
    for section in encoded_df["SectionID"].unique():
        sub_df = encoded_df[encoded_df["SectionID"] == section]
        x = sub_df[["SubjectCode", "TeacherID", "Block"]].astype(np.float32).values

        # Padding if required
        if len(x) < max_len:
            pad = np.zeros((max_len - len(x), 3), dtype=np.float32)
            x = np.vstack([x, pad])
        else:
            x = x[:max_len]

        x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0)
        p = torch.empty(1, 0)

        with torch.no_grad():
            out = model(x_tensor, p).squeeze(0).numpy()

        for i, decoded in enumerate(out):
            best = min(valid_tuples, key=lambda v: np.linalg.norm(decoded - np.array(v)))
            subj_idx, teach_idx, block_idx = best

            subj = inv_subject_map.get(subj_idx, "NA")
            teach = inv_teacher_map.get(teach_idx, "NA")
            block = inv_block_map.get(block_idx, "Unknown")

            # 🧠 Try full match
            match = valid_df[
                (valid_df["SubjectCode"] == subj) &
                (valid_df["TeacherID"] == teach) &
                (valid_df["Block"] == block)
            ]

            # 🔁 Fallback: Subject + Teacher
            if match.empty:
                match = valid_df[
                    (valid_df["SubjectCode"] == subj) &
                    (valid_df["TeacherID"] == teach)
                ]

            # 🔁 Fallback: Subject only
            if match.empty:
                match = valid_df[valid_df["SubjectCode"] == subj]

            # 🪙 Final default if nothing matches
            if not match.empty:
                row = match.iloc[0]
                scheme = row.get("Scheme", "NA")
                subject = row.get("Subject", subj)
                roomtype = row.get("RoomType", "TBD")
            else:
                scheme = "NA"
                subject = subj
                roomtype = "TBD"

            reconstructed_rows.append({
                "SectionID": section,
                "SlotIndex": i,
                "SubjectCode": subj,
                "TeacherID": teach,
                "Block": block,
                "Scheme": scheme,
                "Subject": subject,
                "RoomType": roomtype
            })

    return pd.DataFrame(reconstructed_rows)
