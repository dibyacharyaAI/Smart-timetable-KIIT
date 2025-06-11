import streamlit as st
import pandas as pd
from timetable_pipeline.process import run_full_pipeline
from timetable_pipeline.formatter import format_output

# File Paths
ORIGINAL_FILE = "data/final_transit_fixed.csv"
UPDATED_FILE = "data/updated_from_ui.csv"

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

# 🧠 Sort for readability
def sort_df(df):
    if "SectionID" in df.columns and "SlotIndex" in df.columns:
        return df.sort_values(by=["SectionID", "SlotIndex"]).reset_index(drop=True)
    return df

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📅 Smart Timetable Editor (Drag & Drop Style + Healing Pipeline)")

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

                # Alert for Unknowns
                if (healed_df["Block"] == "Unknown-Block").sum() > 0:
                    st.warning("⚠️ Some rows still have 'Unknown-Block'. Check RoomType mapping or subject data.")

                # Show output in 3 views
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

                # Optional CSV export
                st.download_button(
                    label="📥 Download Final Timetable (CSV)",
                    data=healed_df.to_csv(index=False),
                    file_name="final_timetable_cleaned.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"❌ Error running pipeline: {e}")
else:
    st.stop()
