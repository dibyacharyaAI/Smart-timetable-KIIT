import torch
import numpy as np
import pandas as pd
from timetable_pipeline.model import load_model

def reconstruct_anomalous_sections(df, model_path, valid_tuples, max_len=50):
    model = load_model(model_path)
    reconstructed_rows = []

    for section in df['SectionID'].unique():
        sub_df = df[df['SectionID'] == section]
        x = sub_df[['SubjectIdx', 'TeacherIdx', 'ActivityType']].values
        if len(x) < max_len:
            pad = np.zeros((max_len - len(x), 3))
            x = np.vstack([x, pad])
        else:
            x = x[:max_len]

        x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0)
        p = torch.empty(1, 0)

        with torch.no_grad():
            out = model(x_tensor, p).squeeze(0).numpy()

        for i, decoded in enumerate(out):
            best = min(valid_tuples, key=lambda v: np.linalg.norm(decoded - np.array(v)))
            reconstructed_rows.append({
                'SectionID': section,
                'SlotIndex': i,
                'SubjectIdx': best[0],
                'TeacherIdx': best[1],
                'ActivityType': best[2]
            })

    return pd.DataFrame(reconstructed_rows)
