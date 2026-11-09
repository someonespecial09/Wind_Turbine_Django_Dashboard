import json
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .analytics import load_data, analyze_frame

def _records(df, limit=12):
    return df.tail(limit).replace({float("inf"): None}).to_dict(orient="records")

def _dashboard_context(df):
    df = df.reset_index(drop=True)
    status_counts = df["Anomaly Status"].value_counts()
    health_counts = df["Health Status"].value_counts()
    sample = df.tail(72)
    date_labels = sample["Date/Time"].tolist() if "Date/Time" in sample.columns else list(range(len(sample)))
    return {
        "total_records": len(df),
        "avg_health": round(float(df["Health Score"].mean()), 1),
        "anomaly_count": int((df["Anomaly Status"]=="Anomaly").sum()),
        "warning_count": int((df["Anomaly Status"]=="Warning").sum()),
        "avg_power": round(float(df["LV ActivePower (kW)"].mean()), 1),
        "avg_wind": round(float(df["Wind Speed (m/s)"].mean()), 2),
        "health_labels": json.dumps(list(health_counts.index)),
        "health_values": json.dumps([int(x) for x in health_counts.values]),
        "trend_labels": json.dumps([str(x)[-5:] for x in date_labels]),
        "power_values": json.dumps([round(float(x),2) for x in sample["LV ActivePower (kW)"].fillna(0)]),
        "theory_values": json.dumps([round(float(x),2) for x in sample["Theoretical_Power_Curve (KWh)"].fillna(0)]),
        "wind_values": json.dumps([round(float(x),2) for x in sample["Wind Speed (m/s)"].fillna(0)]),
        "anomaly_labels": json.dumps(["Normal","Warning","Anomaly"]),
        "anomaly_values": json.dumps([int((df["Anomaly Status"]==x).sum()) for x in ["Normal","Warning","Anomaly"]]),
        "recent": _records(df, 8),
        "latest": df.iloc[-1].to_dict() if len(df) else {},
    }

def dashboard(request):
    df = load_data()
    return render(request, "monitoring/dashboard.html", _dashboard_context(df))

def records(request):
    df = load_data().reset_index(drop=True)
    query = request.GET.get("q","").strip().lower()
    status = request.GET.get("status","")
    if query and "Date/Time" in df.columns:
        df = df[df["Date/Time"].astype(str).str.lower().str.contains(query, na=False)]
    if status in ["Normal","Warning","Anomaly"]:
        df = df[df["Anomaly Status"] == status]
    page = max(1, int(request.GET.get("page","1")) if request.GET.get("page","1").isdigit() else 1)
    per_page=30
    total=len(df)
    page_count=max(1,(total+per_page-1)//per_page)
    page=min(page,page_count)
    data=df.iloc[(page-1)*per_page:page*per_page].copy()
    data.insert(0,"Record",data.index+1)
    return render(request,"monitoring/records.html",{"rows":data.to_dict("records"),"q":request.GET.get("q",""),"status":status,"page":page,"page_count":page_count,"total":total})

def alerts(request):
    df=load_data()
    alert_df=df[df["Anomaly Status"]!="Normal"].copy().sort_values("Deviation (%)",ascending=False).head(500)
    alert_df.insert(0,"Record",alert_df.index+1)
    return render(request,"monitoring/alerts.html",{"rows":alert_df.to_dict("records"),"total_alerts":int((df["Anomaly Status"]!="Normal").sum())})

def analyze(request):
    result=None
    if request.method=="POST":
        try:
            if request.FILES.get("csv_file"):
                df=analyze_frame(pd.read_csv(request.FILES["csv_file"]))
                messages.success(request,f"Analyzed {len(df):,} valid rows from your uploaded CSV. Results are shown below.")
                result={"count":len(df),"avg_health":round(float(df["Health Score"].mean()),2),"anomalies":int((df["Anomaly Status"]=="Anomaly").sum()),"warnings":int((df["Anomaly Status"]=="Warning").sum()),"avg_power":round(float(df["LV ActivePower (kW)"].mean()),2)}
            else:
                vals={k:float(request.POST[k]) for k in ["wind_speed","active_power","theoretical_power","wind_direction"]}
                df=pd.DataFrame([{"Wind Speed (m/s)":vals["wind_speed"],"LV ActivePower (kW)":vals["active_power"],"Theoretical_Power_Curve (KWh)":vals["theoretical_power"],"Wind Direction (°)":vals["wind_direction"]}])
                row=analyze_frame(df).iloc[0]
                result={"single":True,"health":round(float(row["Health Score"]),2),"health_status":row["Health Status"],"efficiency":round(float(row["Efficiency (%)"]),2),"deviation":round(float(row["Deviation (%)"]),2),"anomaly":row["Anomaly Status"],"alert":row["Generated Alert"]}
        except Exception as exc:
            messages.error(request,f"Could not analyze input: {exc}")
    return render(request,"monitoring/analyze.html",{"result":result})
