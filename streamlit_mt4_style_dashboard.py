import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Full path to output folder
output_dir = os.path.expanduser("~/manual_autogpt/forex_tuner/output")
available_files = [f for f in os.listdir(output_dir) if f.endswith("_results.csv")]

# Streamlit setup
st.set_page_config(layout="wide", page_title="MT4 Strategy Dashboard")

# Dark theme styling
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
    color: #f5f6fa;
}
[data-testid="metric-container"] {
    background-color: #1e2330;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 10px;
}
thead tr th {
    background-color: #1e2330 !important;
    color: #f5f6fa !important;
}
tbody tr td {
    background-color: #10141f !important;
    color: #f5f6fa !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 MT4-Style Strategy Performance Dashboard")

# File selector
if not available_files:
    st.error("No result files found in /output.")
    st.stop()

selected_file = st.selectbox("Select Strategy Results", available_files)
file_path = os.path.join(output_dir, selected_file)

try:
    df = pd.read_csv(file_path)
    if df.empty or not all(col in df.columns for col in ["net_profit", "win_rate", "max_drawdown", "total_trades"]):
        st.warning(f"`{selected_file}` is empty or missing required columns.")
        st.stop()

    # Metrics
    total_trades = int(df["total_trades"].sum())
    net_profit = df["net_profit"].sum()
    win_rate = df["win_rate"].mean() * 100
    drawdown = df["max_drawdown"].min()
    profit_factor = df["net_profit"].sum() / abs(drawdown) if drawdown < 0 else 0

    # Metric layout
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Total Trades", f"{total_trades}")
    col2.metric("💰 Net Profit", f"${net_profit:,.2f}")
    col3.metric("🎯 Win Rate", f"{win_rate:.1f}%")
    col4.metric("📉 Max Drawdown", f"${drawdown:,.2f}")
    col5.metric("📈 Profit Factor", f"{profit_factor:.2f}")

    # Equity curve
    st.subheader("📈 Equity Curve")
    equity = np.cumsum(df["net_profit"].fillna(0))
    fig, ax = plt.subplots()
    ax.plot(equity, color="#00e6e6", linewidth=2)
    ax.set_title("Simulated Equity Curve")
    ax.set_ylabel("Balance")
    ax.grid(True, linestyle="--", alpha=0.3)
    st.pyplot(fig)

    # Win vs Loss chart
    st.subheader("🔍 Win vs Loss Distribution")
    wins = df[df["net_profit"] > 0].shape[0]
    losses = df[df["net_profit"] < 0].shape[0]
    fig2, ax2 = plt.subplots()
    ax2.bar(["Wins", "Losses"], [wins, losses], color=["#00ffcc", "#ff4d4d"])
    ax2.set_title("Trades Outcome")
    st.pyplot(fig2)

    # Full results table
    st.subheader("📋 Detailed Results")
    styled_df = df[["net_profit", "win_rate", "max_drawdown", "total_trades"]].copy()
    styled_df = styled_df.style.format({
        "net_profit": "${:,.2f}",
        "win_rate": "{:.2%}",
        "max_drawdown": "${:,.2f}",
        "total_trades": "{:.0f}"
    })
    st.dataframe(styled_df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load results: {e}")

