import streamlit as st
import pandas as pd
from timetable_pipeline.process import run_full_pipeline  # Import your pipeline function

# --- Data Loading and Saving ---
DATA_FILE = "data/final_transit_fixed.csv"

@st.cache_data  # Cache the data loading for performance
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            st.warning("CSV file is empty.  Please populate it with data.")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        st.warning(f"CSV file not found: {DATA_FILE}.  Please create it.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.warning("CSV file is empty. Please populate it with data.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
        st.success("Changes saved to CSV!")
    except Exception as e:
        st.error(f"Error saving CSV: {e}")

# --- UI Components ---
st.title("Smart Timetable Editor")

# Load the data
df = load_data()

if not df.empty:
    # Editable Data Grid
    st.header("Edit Timetable Data")
    edited_df = st.data_editor(df, num_rows="dynamic")  # Enable adding rows

    # Run Pipeline Button
    if st.button("Run Timetable Pipeline"):
        with st.spinner("Running pipeline..."):
            try:
                processed_df = run_full_pipeline(edited_df)
                st.success("Pipeline completed successfully!")

                # Display Processed Data
                st.header("Processed Timetable Data")
                st.dataframe(processed_df)

            except Exception as e:
                st.error(f"Error running pipeline: {e}")

    # Save Changes Button
    if st.button("Save Changes to CSV"):
        save_data(edited_df)

    # Display Original and Edited Data (for comparison)
    st.subheader("Original Data")
    st.dataframe(df)

    st.subheader("Edited Data")
    st.dataframe(edited_df)
