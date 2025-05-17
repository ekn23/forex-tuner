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

st.sidebar.header("📤 Upload Market Data")
uploaded_file = st.sidebar.file_uploader("Upload .csv data file", type=["csv"])
if uploaded_file:
    save_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")

st.sidebar.header("⚙️ Strategy")
strategy_files = sorted([f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py") and f != "__init__.py"])
selected_strategy = st.sidebar.selectbox("Choose a strategy", strategy_files)

if selected_strategy and st.sidebar.button("❌ Delete Strategy"):
    os.remove(os.path.join(STRATEGY_DIR, selected_strategy))
    st.sidebar.success(f"Deleted: {selected_strategy}")
    st.rerun()

symbols = sorted(set(f.split("_")[0] for f in os.listdir(DATA_DIR) if f.endswith(".csv")))
selected_symbol = st.sidebar.selectbox("📈 Symbol to Backtest", symbols)

if selected_strategy:
    st.subheader(f"🧠 Strategy Source: `{selected_strategy}`")
    code_path = os.path.join(STRATEGY_DIR, selected_strategy)
    with open(code_path, "r") as f:
        code = f.read()
    edited_code = st.text_area("✏️ Edit Strategy", value=code, height=400, key="edit_code")
    if st.button("💾 Save Strategy"):
        with open(code_path, "w") as f:
            f.write(edited_code)
        st.success("✅ Changes saved.")

if selected_strategy and selected_symbol and st.button("🚀 Run Backtest"):
    strat_name = selected_strategy.replace(".py", "")
    command = f"python3 tuner_runner.py --strategy {strat_name} --symbol {selected_symbol}"
    with st.spinner(f"Running `{strat_name}` on `{selected_symbol}`..."):
        try:
            result = subprocess.check_output(command, shell=True, cwd=os.path.dirname(STRATEGY_DIR), stderr=subprocess.STDOUT)
            st.session_state["last_log"] = result.decode()
            st.success("✅ Backtest complete")
        except subprocess.CalledProcessError as e:
            st.session_state["last_log"] = e.output.decode()
            st.error("❌ Backtest failed")

if st.session_state.get("last_log"):
    st.subheader("📋 Backtest Log Output")
    st.text_area("Execution Log", st.session_state["last_log"], height=300)

if selected_strategy and selected_symbol:
    result_file = os.path.join(OUTPUT_DIR, selected_strategy.replace(".py", "") + "_results.csv")
    if os.path.exists(result_file):
        if os.path.getsize(result_file) == 0:
            st.warning("⚠️ Results file is empty. No trades or output found.")
            st.stop()

        df = pd.read_csv(result_file)

        # ✅ Fixed filter to avoid KeyError
        df_filtered = df[df["symbol"] == selected_symbol] if "symbol" in df.columns else df.copy()

        st.subheader("📈 Results Table")
        st.dataframe(df_filtered, use_container_width=True)

        if "profit" in df_filtered.columns and not df_filtered.empty:
            st.subheader("📊 Profit Bar Chart")
            fig, ax = plt.subplots(figsize=(10, 4))
            df_sorted = df_filtered.sort_values("profit", ascending=False)
            ax.bar(df_sorted.index.astype(str), df_sorted["profit"], color="green")
            ax.set_ylabel("Profit")
            ax.set_xlabel("Parameter Set")
            ax.set_title("Profit by Strategy Variation")
            st.pyplot(fig)

        with open(result_file, "rb") as f:
            st.download_button("📥 Download Results CSV", f, file_name=os.path.basename(result_file), mime="text/csv")
    else:
        st.info("ℹ️ Run a backtest to view results.")

