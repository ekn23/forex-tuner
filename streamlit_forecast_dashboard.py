import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Dummy data
actual_revenue = 6058
target_revenue = 7579
progress_pct = actual_revenue / target_revenue

forecast_df = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
    "Forecast": [500, 550, 480, 700, 950, 900, 300, 400, 850, 870, 600],
    "Actual":   [480, 510, 490, 680, 910, 870, 310, 390, 620, 830, 540]
})

state_df = pd.DataFrame({
    "State": ["AL", "CA", "CO", "DC", "DE", "FL", "IL", "IN", "MA", "MI"],
    "Forecast": [250, 750, 250, 400, 225, 400, 504, 400, 360, 400],
    "Q3 Adj": [-5, -75, 4, 5, 10, 0, -64, 0, 0, 15],
    "Actual": [200, 450, 205, 354, 204, 356, 302, 350, 304, 356],
    "Risk": ["🔴", "🔴", "🟡", "🟡", "🟡", "🟡", "🔴", "🟡", "🟡", "🟡"],
    "Target %": [82, 67, 81, 87, 87, 89, 69, 88, 84, 86]
})

# --- Layout ---
st.set_page_config(layout="wide")
st.title("📊 Forecast Dashboard")

# Revenue Summary
col1, col2 = st.columns([2, 8])
col1.metric("Actual Revenue (thousands)", f"${actual_revenue:,}")
col2.progress(progress_pct)

# Forecast vs Actual Line Chart
st.subheader("Forecast vs Actual (Monthly)")
fig, ax = plt.subplots()
ax.plot(forecast_df["Month"], forecast_df["Forecast"], label="Forecast", marker='o')
ax.plot(forecast_df["Month"], forecast_df["Actual"], label="Actual", marker='o')
ax.set_ylabel("Revenue ($k)")
ax.set_title("Monthly Revenue Forecast vs Actual")
ax.legend()
st.pyplot(fig)

# By State Table
st.subheader("By State Performance")
state_cols = st.columns(5)
with state_cols[0]:
    st.write("### State")
    for s in state_df["State"]:
        st.write(s)
with state_cols[1]:
    st.write("### Forecast")
    for v in state_df["Forecast"]:
        st.write(f"${v}")
with state_cols[2]:
    st.write("### Q3 Adjusted")
    for v in state_df["Q3 Adj"]:
        st.write(f"${v:+}")
with state_cols[3]:
    st.write("### Actual")
    for v in state_df["Actual"]:
        st.write(f"${v}")
with state_cols[4]:
    st.write("### Risk")
    for r in state_df["Risk"]:
        st.write(r)

# Target Achievement Bars
st.subheader("🎯 Target Achieved")
for index, row in state_df.iterrows():
    st.write(f"{row['State']} - {row['Target %']}%")
    st.progress(row['Target %'] / 100)

# Timestamp
st.markdown(f"<div style='text-align:right; color: gray;'>🕒 {pd.Timestamp.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

