from pathlib import Path
import pandas as pd
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "T1.csv"
REQUIRED = ["Wind Speed (m/s)", "LV ActivePower (kW)", "Theoretical_Power_Curve (KWh)", "Wind Direction (°)"]

def analyze_frame(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    for col in REQUIRED:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=REQUIRED).copy()
    theoretical = df["Theoretical_Power_Curve (KWh)"].replace(0, float("nan"))
    df["Efficiency (%)"] = ((df["LV ActivePower (kW)"] / theoretical) * 100).replace([float("inf"), -float("inf")], 0).fillna(0).clip(0,100)
    df["Power Loss (kW)"] = df["LV ActivePower (kW)"] - df["Theoretical_Power_Curve (KWh)"]
    df["Deviation (%)"] = ((df["Power Loss (kW)"].abs() / theoretical) * 100).replace([float("inf"), -float("inf")], 0).fillna(0)
    df["Anomaly Status"] = df["Deviation (%)"].apply(lambda x: "Normal" if x < 10 else ("Warning" if x < 25 else "Anomaly"))
    df["Reliability Score"] = df["Anomaly Status"].map({"Normal":100,"Warning":75,"Anomaly":40})
    df["Stability Score"] = (100-df["Deviation (%)"]).clip(0,100)
    df["Health Score"] = (0.5*df["Efficiency (%)"]+0.3*df["Reliability Score"]+0.2*df["Stability Score"]).clip(0,100)
    df["Health Status"] = df["Health Score"].apply(lambda x: "Excellent" if x>=90 else ("Good" if x>=75 else ("Warning" if x>=60 else "Critical")))
    df["Generated Alert"] = df["Health Status"].map({"Excellent":"Healthy Operation","Good":"Monitor Performance","Warning":"Performance Anomaly Detected","Critical":"Critical Maintenance Required"})
    if "Date/Time" in df.columns:
        df["Date/Time"] = df["Date/Time"].astype(str)
    return df

def load_data():
    return analyze_frame(pd.read_csv(DATA_PATH))
