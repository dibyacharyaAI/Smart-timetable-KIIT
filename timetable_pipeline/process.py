# timetable_pipeline/process.py

import pandas as pd

from timetable_pipeline.model import load_model
from timetable_pipeline.heal import reconstruct_anomalous_sections
from timetable_pipeline.conflict_solver import solve_teacher_conflict
from timetable_pipeline.transit import build_transit_map, repair_transit_violations
from timetable_pipeline.formatter import format_admin_view

def run_full_pipeline(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the entire Smart Timetable pipeline on uploaded CSV data:
    - Healing anomalies
    - Resolving teacher conflicts
    - Assigning blocks based on activity
    - Fixing transit violations
    - Returning final DataFrame (UI-ready)
    """
    # ✅ Step 1: Extract valid tuples from input for reconstruction
    valid_tuples = list(
        input_df[['SubjectCode', 'TeacherID', 'Block']]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    # ✅ Step 2: Heal anomalous section rows using autoencoder
    healed_df = reconstruct_anomalous_sections(
        input_df,
        model_path="data/timetable_autoencoder150.pt",
        valid_tuples=valid_tuples
    )

    # ✅ Step 3: Resolve teacher assignment conflicts
    teacher_fixed_df = solve_teacher_conflict(healed_df)

    # ✅ Step 4: Attach RoomType from activity table → map to Block
    activity_df = pd.read_excel("data/activities_table.xlsx")
    merged_df = teacher_fixed_df.merge(
        activity_df[['Subject', 'RoomType']],
        left_on="SubjectCode",
        right_on="Subject",
        how="left"
    )
    roomtype_to_block = {
        "Classroom": "Block-CAM",
        "Lab": "Block-LAB",
        "Seminar": "Block-SEMINAR"
    }
    merged_df["Block"] = merged_df["RoomType"].map(roomtype_to_block).fillna("Unknown-Block")

    # ✅ Step 5: Apply transit time constraints & fix violations
    transit_df = pd.read_excel("data/updated_transit_time_constraints.xlsx")
    transit_map = build_transit_map(transit_df)
    final_df = repair_transit_violations(merged_df, transit_map)

    # ✅ Step 6: Return processed DataFrame for UI response
    return final_df
