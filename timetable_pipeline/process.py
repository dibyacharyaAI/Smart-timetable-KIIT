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
    3. Map RoomType → Block (based on transit file values)
    4. Apply transit time repair
    5. Inject TeacherName
    6. Return final cleaned DataFrame
    """

    # Step 1: Create valid encoded input combinations
    valid_tuples = list(
        input_df[["SubjectCode", "TeacherID", "Block"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    # Step 2: Heal anomalies
    healed_df = reconstruct_anomalous_sections(
        input_df,
        model_path="data/timetable_autoencoder150.pt",
        valid_tuples=valid_tuples,
        valid_df=input_df
    )

    # Step 3: Solve conflicts
    teacher_fixed_df = solve_teacher_conflict(healed_df)

    # Step 4: Normalize RoomType and map to Block
    teacher_fixed_df["RoomType"] = teacher_fixed_df["RoomType"].astype(str).str.strip().str.lower()

    roomtype_to_block = {
        "cam 3 chem lab": "Block-CAM3-CHEM",
        "cam 8 em lab": "Block-CAM8-EM",
        "cam 8 workshop": "Block-CAM8-WORK",
        "camp 3 block a": "Block-CAMP3-A",
        "camp 3 block e": "Block-CAMP3-E",
        "campus 17 (class)": "Block-C17",
        "campus 3 (physics/ed)": "Block-C3-ED",
        "campus 8 (class)": "Block-C8",
        "cam 12 (class)": "Block-C12",
        "cam 13 sy": "Block-C13",
        "cam 3 (class)": "Block-C3",
        "cam-3 lab": "Block-C3-LAB",
        "block a-dl and b-wl": "Block-DL-WL",
        "block c-wl": "Block-C-WL"
    }

    teacher_fixed_df["Block"] = teacher_fixed_df["RoomType"].map(roomtype_to_block).fillna("Unknown-Block")

    # Step 5: Fix transit violations
    transit_df = pd.read_excel("data/updated_transit_time_constraints.xlsx")
    transit_map = build_transit_map(transit_df)
    final_df = repair_transit_violations(teacher_fixed_df, transit_map)

    # Step 6: Add TeacherName (if mapping file exists)
    try:
        teacher_map_df = pd.read_excel("data/structured_teacher_mapping.xlsx")
        teacher_map = dict(zip(teacher_map_df["TeacherID"], teacher_map_df["TeacherName"]))
        final_df["TeacherName"] = final_df["TeacherID"].map(teacher_map).fillna("Unknown Faculty")
    except Exception as e:
        final_df["TeacherName"] = final_df["TeacherID"]  # Fallback

    return final_df
