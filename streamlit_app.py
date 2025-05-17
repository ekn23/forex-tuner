import os
import subprocess
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

STRATEGY_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/strategies")
OUTPUT_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/output")
DATA_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/data")

st.set_page_config(page_title="Forex Strategy Tuner", layout="wide")
st.title("📊 Forex Strategy Tuner Dashboard")

# --- Upload CSV File ---
st.sidebar.header("📤 Upload Market Data")
uploaded_file = st.sidebar.file_uploader("Upload .csv data file", type=["csv"])
if uploaded_file:
    save_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")

# --- Strategy Picker ---
st.sidebar.header("⚙️ Strategy")
strategy_files = [f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py") and f != "__init__.py"]
selected_strategy = st.sidebar.selectbox("Choose a strategy", strategy_files)

# --- Delete Strategy ---
if selected_strategy and st.sidebar.button("❌ Delete Strategy"):
    os.remove(os.path.join(STRATEGY_DIR, selected_strategy))
    st.sidebar.success(f"Deleted: {selected_strategy}")
    st.experimental_rerun()

# --- Symbol Picker ---
symbols = sorted(set(f.split("_")[0] for f in os.listdir(DATA_DIR) if f.endswith(".csv")))
selected_symbol = st.sidebar.selectbox("📈 Symbol to Backtest", symbols)

# --- View/Edit Source Code ---
if selected_strategy:
    st.subheader(f"🧠 Strategy Source: `{selected_strategy}`")
    code_path = os.path.join(STRATEGY_DIR, selected_strategy)
    with open(code_path) as f:
        code = f.read()
    edited_code = st.text_area("✏️ Edit Strategy", value=code, height=400, key="edit_code")
    if st.button("💾 Save Strategy"):
        with open(code_path, "w") as f:
            f.write(edited_code)
        st.success("✅ Changes saved!")

# --- Run Strategy ---
if selected_strategy and selected_symbol and st.button("🚀 Run Backtest"):
    strat_name = selected_strategy.replace(".py", "")
    command = f"python3 tuner_runner.py --strategy {strat_name} --symbol {selected_symbol}"
    with st.spinner(f"Running `{strat_name}` on `{selected_symbol}`..."):
        try:
            result = subprocess.check_output(command, shell=True, cwd=os.path.dirname(STRATEGY_DIR), stderr=subprocess.STDOUT)
            st.success("✅ Backtest complete")
            st.text_area("📋 Log Output", result.decode(), height=300)
        except subprocess.CalledProcessError as e:
            st.error("❌ Backtest failed")
            st.text_area("Error", e.output.decode(), height=300)

# --- Results Viewer ---
if selected_strategy and selected_symbol:
    result_file = os.path.join(OUTPUT_DIR, selected_strategy.replace(".py", "") + "_results.csv")
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)

        # Filter by symbol (if symbol column exists)
        if "symbol" in df.columns:
            df = df[df["symbol"] == selected_symbol]

        st.subheader("📈 Backtest Results Table")

        # New Filters
        col1, col2, col3 = st.columns(3)
        min_win_rate = col1.slider("Min Win Rate", 0.0, 1.0, 0.5, 0.01)
        max_drawdown = col2.slider("Max Drawdown", -100.0, 0.0, -50.0, 1.0)
        sort_metric = col3.selectbox("Sort By", ["net_profit", "win_rate", "max_drawdown"])

        df_filtered = df[(df["win_rate"] >= min_win_rate) & (df["max_drawdown"] >= max_drawdown)]
        df_sorted = df_filtered.sort_values(by=sort_metric, ascending=False)

        st.dataframe(df_sorted.head(10), use_container_width=True)

        # Show best result summary
        if not df_sorted.empty:
            st.subheader("📌 Best Result Summary")
            best = df_sorted.iloc[0]
            st.json(best.to_dict())

        # Profit bar chart (if profit column exists)
        if "profit" in df_sorted.columns and not df_sorted.empty:
            st.subheader("📊 Profit Chart")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df_sorted.index.astype(str), df_sorted["profit"], color="green")
            ax.set_ylabel("Profit")
            ax.set_xlabel("Combo #")
            ax.set_title("Profit by Parameter Set")
            st.pyplot(fig)

        # Download CSV
        st.download_button(
            "📥 Download Full Results",
            data=df.to_csv(index=False),
            file_name=os.path.basename(result_file),
            mime="text/csv"
        )
    else:
        st.info("Run a backtest to see results.")

