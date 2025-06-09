import pandas as pd

def build_transit_map(transit_df):
    transit_df['RequiredGap'] = (transit_df['TRANSIT TIME(Minutes)'] / 60).apply(lambda x: max(1, round(x))).astype(int)
    transit_map = {}
    for _, row in transit_df.iterrows():
        a, b, g = row['LOCATION A'].strip(), row['LOCATION B'].strip(), row['RequiredGap']
        transit_map.setdefault(a, {})[b] = g
        transit_map.setdefault(b, {})[a] = g
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
                gap = (row['SlotIndex'] + shift) - prev['SlotIndex']
                required = transit_map.get(prev['Block'], {}).get(row['Block'], 0)
                if gap < required:
                    shift += (required - gap)
            row['SlotIndex'] += shift
            new_rows.append(row)
        return pd.DataFrame(new_rows)

    for group_col in ['TeacherID', 'SectionID']:
        for val in df[group_col].unique():
            sub_df = df[df[group_col] == val]
            repaired = shift_schedule(sub_df)
            fixed_rows.append(repaired)

    final_df = pd.concat(fixed_rows, ignore_index=True)
    return final_df.drop_duplicates(subset=["SectionID", "SlotIndex"])
