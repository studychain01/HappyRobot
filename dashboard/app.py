import os, requests, pandas as pd, streamlit as st

API_BASE = os.getenv("API_BASE", "https://happyrobot-trucking-loadsapi.onrender.com")
API_KEY = os.getenv("API_KEY", "mysecret")

st.title("HappyRobot — Inbound Loads Dashboard")

st.caption(f"API_BASE={API_BASE}")
try:
    resp = requests.get(f"{API_BASE}/loads", headers={"x-api-key": API_KEY}, timeout=15)
    if not resp.ok:
        st.error(f"Request failed: {resp.status_code} {resp.reason}")
        st.code(resp.text)
        data = []
    else:
        payload = resp.json()
        data = payload.get("results", [])
        st.success(f"Found {len(data)} loads")
except Exception as e:
    st.exception(e)
    data = []

df = pd.DataFrame(data)

st.subheader("Loads")
st.dataframe(df, use_container_width=True)

if not df.empty:
    st.subheader("Equipment mix")
    st.bar_chart(df["equipment_type"].value_counts())

    st.subheader("Avg miles by origin (top 10)")
    st.bar_chart(df.groupby("origin")["miles"].mean().sort_values(ascending=False).head(10))