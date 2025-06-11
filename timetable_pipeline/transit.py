import pandas as pd

def build_transit_map(transit_df):
    # Convert transit minutes to slot gaps (1 hour = 1 slot)
    transit_df['RequiredGap'] = (transit_df['TRANSIT TIME(Minutes)'] / 60).apply(lambda x: max(1, round(x))).astype(int)
    transit_map = {}

    for _, row in transit_df.iterrows():
        a = str(row['LOCATION A']).strip().lower()
        b = str(row['LOCATION B']).strip().lower()
        g = row['RequiredGap']
        transit_map.setdefault(a, {})[b] = g
        transit_map.setdefault(b, {})[a] = g  # Bi-directional gap
    return transit_map

def repair_transit_violations(df, transit_map):
    fixed_rows = []

    def shift_schedule(sub_df):
        sub_df = sub_df.sort_values('SlotIndex').reset_index(drop=True)
        new_rows = []
        shift = 0
        for i in range(len(sub_df)):
            row = sub_df.loc[i].copy()
            if i > 0:
                prev = new_rows[-1]
                prev_block = str(prev['Block']).strip().lower()
                curr_block = str(row['Block']).strip().lower()
                gap = row['SlotIndex'] + shift - prev['SlotIndex']
                required = transit_map.get(prev_block, {}).get(curr_block, 0)
                if gap < required:
                    shift += (required - gap)
            row['SlotIndex'] += shift
            new_rows.append(row)
        return pd.DataFrame(new_rows)

    # Transit time matters only across same teacher's sessions
    for tid in df["TeacherID"].astype(str).unique():
        sub_df = df[df["TeacherID"].astype(str) == tid]
        repaired = shift_schedule(sub_df)
        fixed_rows.append(repaired)

    final_df = pd.concat(fixed_rows, ignore_index=True)

    # Drop potential duplicates caused by shifting
    final_df = final_df.drop_duplicates(subset=["SectionID", "SlotIndex"], keep="first")

    return final_df
