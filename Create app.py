
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from financial_analyzer import analyze_financial_data
from ai_analyst import explain_financial_trends, flush_langfuse


st.set_page_config(
    page_title="AI Financial Statement Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Financial Statement Analyst")
st.caption(
    "Python + Pandas + Gemini AI + Langfuse"
)

st.write(
    "Upload a company's financial statements to calculate "
    "financial ratios and understand financial trends."
)

# Demo dataset
sample_data = pd.DataFrame({
    "Year": [2023, 2024, 2025],
    "Revenue": [1000000, 1250000, 1500000],
    "Net_Income": [100000, 150000, 210000],
    "Current_Assets": [400000, 500000, 650000],
    "Current_Liabilities": [250000, 280000, 300000],
    "Total_Debt": [300000, 320000, 350000],
    "Shareholders_Equity": [500000, 600000, 750000],
    "Total_Assets": [800000, 950000, 1200000],
})

st.sidebar.header("Data source")

use_demo = st.sidebar.checkbox(
    "Use sample financial data",
    value=True,
)

uploaded_file = st.sidebar.file_uploader(
    "Or upload a CSV file",
    type=["csv"],
)

df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Unable to read the CSV: {exc}")
elif use_demo:
    df = sample_data.copy()

if df is None:
    st.info("Choose the sample data or upload a financial CSV.")
    st.stop()

st.subheader("Financial Statement Data")
st.dataframe(df, use_container_width=True)

try:
    results = analyze_financial_data(df)
except (ValueError, TypeError) as exc:
    st.error(f"Data validation error: {exc}")
    st.stop()

st.subheader("Calculated Financial Ratios")

ratio_columns = [
    "Current_Ratio",
    "Net_Profit_Margin_Percent",
    "Debt_to_Equity_Ratio",
    "ROA_Percent",
]

display_names = {
    "Current_Ratio": "Current Ratio",
    "Net_Profit_Margin_Percent": "Net Profit Margin (%)",
    "Debt_to_Equity_Ratio": "Debt-to-Equity Ratio",
    "ROA_Percent": "Return on Assets (%)",
}

st.dataframe(
    results[["Year"] + ratio_columns].rename(
        columns=display_names
    ).round(2),
    use_container_width=True,
)

# Latest year metrics
latest = results.iloc[-1]

st.subheader(f"Latest Year Overview: {latest['Year']}")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"{latest['Revenue']:,.0f}",
)

c2.metric(
    "Net Income",
    f"{latest['Net_Income']:,.0f}",
)

c3.metric(
    "Current Ratio",
    "N/A" if pd.isna(latest["Current_Ratio"])
    else f"{latest['Current_Ratio']:.2f}",
)

c4.metric(
    "Net Profit Margin",
    "N/A" if pd.isna(latest["Net_Profit_Margin_Percent"])
    else f"{latest['Net_Profit_Margin_Percent']:.2f}%",
)

# Financial trends
st.subheader("Financial Performance Trends")

selected_ratio = st.selectbox(
    "Choose a ratio",
    ratio_columns,
    format_func=lambda col: display_names[col],
)

fig, ax = plt.subplots()

ax.plot(
    results["Year"].astype(str),
    results[selected_ratio],
    marker="o",
)

ax.set_title(display_names[selected_ratio])
ax.set_xlabel("Year")
ax.set_ylabel(display_names[selected_ratio])
ax.grid(True)

st.pyplot(fig)
plt.close(fig)

# AI analysis
st.subheader("🤖 AI Financial Analysis")

if st.button("Generate AI Explanation", type="primary"):
    summary_columns = [
        "Year",
        "Revenue",
        "Net_Income",
        "Current_Ratio",
        "Net_Profit_Margin_Percent",
        "Debt_to_Equity_Ratio",
        "ROA_Percent",
    ]

    summary = results[summary_columns].round(2).to_string(
        index=False
    )

    try:
        with st.spinner("Analyzing financial trends..."):
            explanation = explain_financial_trends(summary)

        st.markdown(explanation)
        st.success("AI analysis completed.")

    except Exception as exc:
        st.error(f"AI analysis failed: {exc}")

    finally:
        flush_langfuse()

st.caption(
    "Educational tool only. Verify calculations and consult "
    "a qualified professional for consequential decisions."
)
