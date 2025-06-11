import pandas as pd

from timetable_pipeline.model import load_model
from timetable_pipeline.heal import reconstruct_anomalous_sections
from timetable_pipeline.conflict_solver import solve_teacher_conflict
from timetable_pipeline.transit import build_transit_map, repair_transit_violations

def run_full_pipeline(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Full Smart Timetable pipeline:
    1. Heal anomalies via autoencoder
    2. Resolve teacher conflicts (CP-SAT)
    3. Apply transit rules
    4. Return clean UI-ready DataFrame
    """

    # Step 1: Prepare valid encoded input combinations
    valid_tuples = list(
        input_df[["SubjectCode", "TeacherID", "Block"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    # Step 2: Heal anomalies using autoencoder model
    healed_df = reconstruct_anomalous_sections(
        input_df,
        model_path="data/timetable_autoencoder150.pt",
        valid_tuples=valid_tuples,
        valid_df=input_df  # 🔁 Needed to fetch missing fields
    )

    # Step 3: Resolve teacher conflicts using constraint programming
    teacher_fixed_df = solve_teacher_conflict(healed_df)

    # Step 4: Fix transit time violations
    transit_df = pd.read_excel("data/updated_transit_time_constraints.xlsx")
    transit_map = build_transit_map(transit_df)
    final_df = repair_transit_violations(teacher_fixed_df, transit_map)

    # Step 5: Return final cleaned timetable
    return final_df
