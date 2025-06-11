import torch
import numpy as np
import pandas as pd
from timetable_pipeline.model import load_model

def reconstruct_anomalous_sections(df, model_path, valid_tuples=None, valid_df=None, max_len=50):
    model = load_model(model_path)
    reconstructed_rows = []

    # Normalize key columns
    df["SubjectCode"] = df["SubjectCode"].astype(str).str.strip()
    df["TeacherID"] = df["TeacherID"].astype(str).str.strip()
    df["Block"] = df["Block"].astype(str).str.strip()

    # Encode categorical columns
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

    # Prepare valid encoded tuples
    valid_tuples = list(
        encoded_df[["SubjectCode", "TeacherID", "Block"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    if valid_df is None:
        raise ValueError("valid_df is required for reconstructing contextual fields.")

    # Normalize valid_df for lookup
    valid_df["SubjectCode"] = valid_df["SubjectCode"].astype(str).str.strip()
    valid_df["TeacherID"] = valid_df["TeacherID"].astype(str).str.strip()
    valid_df["Block"] = valid_df["Block"].astype(str).str.strip()

    # Section-wise healing
    for section in encoded_df['SectionID'].unique():
        sub_df = encoded_df[encoded_df['SectionID'] == section]
        x = sub_df[['SubjectCode', 'TeacherID', 'Block']].astype(np.float32).values

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

            # Match original fields from unencoded valid_df
            match = valid_df[
                (valid_df["SubjectCode"] == subj) &
                (valid_df["TeacherID"] == teach) &
                (valid_df["Block"] == block)
            ]

            if not match.empty:
                row = match.iloc[0]
                scheme = row.get("Scheme", "NA")
                subject = row.get("Subject", "Unknown")
                roomtype = row.get("RoomType", "TBD")
            else:
                scheme, subject, roomtype = "NA", "Unknown", "TBD"

            reconstructed_rows.append({
                'SectionID': section,
                'SlotIndex': i,
                'SubjectCode': subj,
                'TeacherID': teach,
                'Block': block,
                'Scheme': scheme,
                'Subject': subject,
                'RoomType': roomtype
            })

    return pd.DataFrame(reconstructed_rows)
