import pandas as pd
from ortools.sat.python import cp_model

def solve_teacher_conflict(df):
    sections = df["SectionID"].unique().tolist()
    slots = sorted(df["SlotIndex"].unique())
    teachers = df["TeacherID"].unique().tolist()
    subjects = df["SubjectCode"].unique().tolist()
    T, S = len(teachers), len(subjects)

    teacher_map = {t: i for i, t in enumerate(teachers)}
    subject_map = {s: i for i, s in enumerate(subjects)}

    all_section_dfs = []

    for sec in sections:
        model = cp_model.CpModel()
        X = {slot: model.NewIntVar(0, T * S - 1, f"x_{sec}_{slot}") for slot in slots}
        model.AddAllDifferent(list(X.values()))

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            output = []
            for slot in slots:
                val = solver.Value(X[slot])
                t_idx, s_idx = divmod(val, S)
                teacher = teachers[t_idx]
                subject = subjects[s_idx]

                # Match back to original row for context
                original_match = df[
                    (df["SectionID"] == sec) &
                    (df["SubjectCode"] == subject) &
                    (df["TeacherID"] == teacher)
                ]

                if not original_match.empty:
                    row = original_match.iloc[0]
                    scheme = row.get("Scheme", "NA")
                    subject_name = row.get("Subject", "Unknown")
                    roomtype = row.get("RoomType", "TBD")
                    block = row.get("Block", "Unknown-Block")
                    teacher_name = row.get("TeacherName", "Unknown")
                else:
                    scheme = "NA"
                    subject_name = "Unknown"
                    roomtype = "TBD"
                    block = "Unknown-Block"
                    teacher_name = "Unknown"

                output.append({
                    "SectionID": sec,
                    "SlotIndex": slot,
                    "SubjectCode": subject,
                    "TeacherID": teacher,
                    "TeacherName": teacher_name,
                    "Scheme": scheme,
                    "Subject": subject_name,
                    "RoomType": roomtype,
                    "Block": block
                })

            result_df = pd.DataFrame(output)
            all_section_dfs.append(result_df)

    return pd.concat(all_section_dfs, ignore_index=True)
