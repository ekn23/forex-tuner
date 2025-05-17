import os
import subprocess
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Paths
STRATEGY_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/strategies")
OUTPUT_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/output")
DATA_DIR = os.path.expanduser("~/manual_autogpt/forex_tuner/data")

# Layout
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
    st.rerun()

# --- Symbol Picker ---
symbols = sorted(set(f.split("_")[0] for f in os.listdir(DATA_DIR) if f.endswith(".csv")))
selected_symbol = st.sidebar.selectbox("📈 Symbol to Backtest", symbols)

# --- View/Edit Strategy Code ---
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

# --- Show Backtest Results ---
if selected_strategy and selected_symbol:
    result_file = os.path.join(OUTPUT_DIR, selected_strategy.replace(".py", "") + "_results.csv")
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)
        df_filtered = df[df["symbol"] == selected_symbol]

        st.subheader("📈 Backtest Results Table")
        st.dataframe(df_filtered)

        if "profit" in df_filtered.columns and not df_filtered.empty:
            st.subheader("📊 Profit Chart")
            fig, ax = plt.subplots(figsize=(10, 4))
            df_sorted = df_filtered.sort_values("profit", ascending=False)
            ax.bar(df_sorted.index.astype(str), df_sorted["profit"], color="green")
            ax.set_ylabel("Profit")
            ax.set_xlabel("Combo #")
            ax.set_title("Profit by Parameter Set")
            st.pyplot(fig)

        # --- Download Button ---
        with open(result_file, "rb") as f:
            st.download_button("📥 Download Results CSV", f, file_name=os.path.basename(result_file), mime="text/csv")
    else:
        st.info("ℹ️ Run a backtest to see results.")
