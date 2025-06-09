import pandas as pd
from timetable_pipeline.model import load_model
from timetable_pipeline.heal import reconstruct_anomalous_sections
from timetable_pipeline.conflict_solver import solve_teacher_conflict
from timetable_pipeline.transit import build_transit_map, repair_transit_violations
from timetable_pipeline.formatter import format_admin_view

def run_full_pipeline(input_df):
    # Step 1: Anomaly detection skipped — assume full healing always triggered
    valid_tuples = list(input_df[['SubjectIdx', 'TeacherIdx', 'ActivityType']].drop_duplicates().itertuples(index=False, name=None))

    # Step 2: Heal
    healed_df = reconstruct_anomalous_sections(input_df, "sample_data/timetable_autoencoder150.pt", valid_tuples)

    # Step 3: Teacher conflict fix
    teacher_fixed_df = solve_teacher_conflict(healed_df)

    # Step 4: Merge activity info (optional) and map Block from RoomType
    activity_df = pd.read_excel("sample_data/activities_table.xlsx")
    full_df = teacher_fixed_df.merge(activity_df[['Subject', 'RoomType']], left_on='SubjectCode', right_on='Subject', how='left')
    roomtype_to_block = {'Classroom': 'Block-CAM', 'Lab': 'Block-LAB', 'Seminar': 'Block-SEMINAR'}
    full_df['Block'] = full_df['RoomType'].map(roomtype_to_block).fillna("Unknown-Block")

    # Step 5: Transit repair
    transit_df = pd.read_excel("sample_data/updated_transit_time_constraints.xlsx")
    transit_map = build_transit_map(transit_df)
    transit_fixed_df = repair_transit_violations(full_df, transit_map)

    # Step 6: Return UI-ready view (admin format)
    return format_admin_view(transit_fixed_df)
