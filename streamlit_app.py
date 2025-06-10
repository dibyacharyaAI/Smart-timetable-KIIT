import sys
sys.modules['torch._classes'] = None

import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


import streamlit as st
import pandas as pd
from timetable_pipeline.process import run_full_pipeline

st.title("Smart Timetable Processor")

uploaded_file = st.file_uploader("Upload modified timetable CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    result = run_full_pipeline(df)
    st.success("Timetable processed successfully!")
    st.json(result)
