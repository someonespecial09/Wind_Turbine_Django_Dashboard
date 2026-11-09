# TurbineIQ — Django Wind Turbine SCADA Dashboard

A Django web dashboard built around the supplied mini-project dataset and notebook logic for SCADA-based wind turbine performance monitoring and anomaly detection.

## Features
- Overview dashboard with KPI cards and interactive charts
- Actual vs theoretical power trend, anomaly distribution, and health status chart
- SCADA record table with date search, status filters, and pagination
- Alerts page sorted by deviation, with maintenance recommendations
- Manual single-record assessment
- CSV upload assessment
- Uses the same core project formulas: efficiency, absolute power deviation, anomaly bands, reliability/stability scores, and weighted health score

## Requirements
- Python 3.10 or newer (Python 3.12 recommended)
- Internet connection for Chart.js and Google Fonts CDN assets (dashboard layout still loads without fonts; charts need Chart.js). No Node.js required.

## Run on Windows (PowerShell)
1. Extract the ZIP.
2. Open PowerShell in the extracted `Wind_Turbine_Django_Dashboard` folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Create the local database tables and start the server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

6. Open `http://127.0.0.1:8000/` in your browser.

## Dataset
The included `data/T1.csv` is the original 50,530-row dataset from the supplied ZIP. The dashboard computes its metrics from this CSV when a page is requested. `data/wind_turbine.csv` is also included as the smaller sample file.

## CSV upload headers
Required:
- `Wind Speed (m/s)`
- `LV ActivePower (kW)`
- `Theoretical_Power_Curve (KWh)`
- `Wind Direction (°)`

`Date/Time` is optional. The uploaded file is analyzed for that request and does not overwrite the bundled dataset.

## Important interpretation note
This is a dataset-driven research/demo dashboard, not live turbine telemetry. The Normal/Warning/Anomaly flags are rule-based deviation indicators, not proof of a physical fault. The secret key and settings are for local development only; harden them before deployment.
