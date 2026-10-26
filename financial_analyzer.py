
import pandas as pd


REQUIRED_COLUMNS = [
    "Year",
    "Revenue",
    "Net_Income",
    "Current_Assets",
    "Current_Liabilities",
    "Total_Debt",
    "Shareholders_Equity",
    "Total_Assets",
]


def analyze_financial_data(df):
    # Check required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    # Convert financial values to numeric
    numeric_columns = REQUIRED_COLUMNS[1:]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[numeric_columns].isna().any().any():
        raise ValueError(
            "Financial columns contain missing or invalid values. "
            "Please clean the CSV before analysis."
        )

    if df["Year"].duplicated().any():
        raise ValueError("Each year must appear only once.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError(
            "Negative financial values are not supported "
            "by this starter version."
        )

    # Calculate financial ratios safely
    def safe_divide(numerator, denominator):
        return numerator.div(denominator.where(denominator != 0))

    df["Current_Ratio"] = safe_divide(
        df["Current_Assets"], df["Current_Liabilities"]
    )

    df["Net_Profit_Margin_Percent"] = (
        safe_divide(df["Net_Income"], df["Revenue"]) * 100
    )

    df["Debt_to_Equity_Ratio"] = safe_divide(
        df["Total_Debt"], df["Shareholders_Equity"]
    )

    df["ROA_Percent"] = (
        safe_divide(df["Net_Income"], df["Total_Assets"]) * 100
    )

    return df.sort_values("Year").reset_index(drop=True)
