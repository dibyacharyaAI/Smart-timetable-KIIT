import streamlit as st
import pandas as pd
from timetable_pipeline.process import run_full_pipeline
from timetable_pipeline.formatter import format_output

# File Paths
ORIGINAL_FILE = "data/final_transit_fixed.csv"
UPDATED_FILE = "data/updated_from_ui.csv"
TEACHER_MAP_FILE = "data/structured_teacher_mapping.xlsx"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(ORIGINAL_FILE)
        if df.empty:
            st.warning("CSV file is empty.")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.warning("CSV file not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

def save_data(df):
    try:
        df.to_csv(UPDATED_FILE, index=False)
        st.success("✅ Changes saved to updated_from_ui.csv!")
    except Exception as e:
        st.error(f"Error saving CSV: {e}")

def sort_df(df):
    if "SectionID" in df.columns and "SlotIndex" in df.columns:
        return df.sort_values(by=["SectionID", "SlotIndex"]).reset_index(drop=True)
    return df

# Add human-readable columns
def enhance_readability(df):
    # Day & Time
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    df["Day"] = df["SlotIndex"] // 8
    df["StartHour"] = 8 + (df["SlotIndex"] % 8)
    df["EndHour"] = df["StartHour"] + 1
    df["Day"] = df["Day"].apply(lambda d: day_names[d] if d < len(day_names) else "Unknown")
    df["Time"] = df["StartHour"].astype(str) + ":00 - " + df["EndHour"].astype(str) + ":00"

    # Teacher Name mapping
    try:
        teacher_map_df = pd.read_excel(TEACHER_MAP_FILE)
        teacher_map = dict(zip(teacher_map_df["TeacherID"], teacher_map_df["TeacherName"]))
        df["TeacherName"] = df["TeacherID"].map(teacher_map).fillna("Unknown Faculty")
    except Exception as e:
        st.warning(f"⚠️ Could not load teacher mapping: {e}")
        df["TeacherName"] = df["TeacherID"]

    return df

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📅 Smart Timetable Editor (Human-Readable View + Healing Pipeline)")

df = load_data()
df = sort_df(df)

if not df.empty:
    st.subheader("✍️ Editable Timetable")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Edited CSV"):
            save_data(edited_df)

    with col2:
        if st.button("⚙️ Run Full Healing Pipeline"):
            try:
                st.info("Running full healing + conflict-solving pipeline...")
                healed_df = run_full_pipeline(edited_df)

                # Warn for Unknown-Block
                if (healed_df["Block"] == "Unknown-Block").sum() > 0:
                    st.warning("⚠️ Some rows still have 'Unknown-Block'. Check RoomType mapping or subject data.")

                # Enhance for readability
                healed_df = enhance_readability(healed_df)

                # Format 3 views
                section_df = format_output(healed_df, mode="section")
                teacher_df = format_output(healed_df, mode="teacher")
                admin_df = format_output(healed_df, mode="admin")

                st.success("✅ Pipeline completed and formatted successfully!")

                tab1, tab2, tab3 = st.tabs(["🏫 Section-wise", "👨‍🏫 Teacher-wise", "🗂️ Admin-wise"])

                with tab1:
                    st.dataframe(section_df, use_container_width=True)

                with tab2:
                    st.dataframe(teacher_df, use_container_width=True)

                with tab3:
                    st.dataframe(admin_df, use_container_width=True)

                # Export button
                st.download_button(
                    label="📥 Download Final Human-Readable Timetable",
                    data=healed_df.to_csv(index=False),
                    file_name="final_timetable_readable.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"❌ Error running pipeline: {e}")
else:
    st.stop()
