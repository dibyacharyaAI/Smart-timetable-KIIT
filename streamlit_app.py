

# === Mac GPU fallback safe mode ===
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# === App code ===
import streamlit as st
import pandas as pd
from timetable_pipeline.process import run_full_pipeline

st.set_page_config(page_title="Smart Timetable", layout="centered")
st.title("📘 Smart Timetable Processor")

uploaded_file = st.file_uploader("📤 Upload modified timetable CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        with st.spinner("⏳ Processing with full pipeline..."):
            result = run_full_pipeline(df)
        st.success("✅ Timetable processed successfully!")
        st.subheader("📋 Final Output (UI-Ready JSON):")
        st.json(result)
    except Exception as e:
        st.error(f"❌ Error processing timetable: {str(e)}")
