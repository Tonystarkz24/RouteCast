import os

DEFAULT_ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRiYmMyZDU0MmRjMjQ4YWU4MTZlMmVhMWFiMzk2NTM1IiwiaCI6Im11cm11cjY0In0="

ORS_API_KEY = os.environ.get("ORS_API_KEY", DEFAULT_ORS_KEY)

try:
    import streamlit as st
    if hasattr(st, "secrets") and "ORS_API_KEY" in st.secrets:
        ORS_API_KEY = st.secrets["ORS_API_KEY"]
except Exception:
    pass