"""
PaySafe India — Flask demo: UPI transaction fraud checker.

Run (from the project root, after running 06_SupervisedModels.py):
    python app/app.py          ->  http://127.0.0.1:5000

The page is a thin layer over the saved scikit-learn pipeline (models/fraud_model.joblib):
the SAME preprocessing (impute -> scale -> one-hot) used in training is applied to the form input.
Fields left untouched default to the *typical legitimate* value, so an empty form scores as safe.
"""
import json
import math
import sys
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "fraud_model.joblib"
META_PATH = ROOT / "models" / "model_meta.json"

if not MODEL_PATH.exists():
    sys.exit("Model not found. Run 06_SupervisedModels.py first (it saves models/fraud_model.joblib).")

model = joblib.load(MODEL_PATH)
meta = json.loads(META_PATH.read_text())
NUMERIC, CATEGORICAL = meta["numeric_features"], meta["categorical_features"]
MEDIAN, THRESHOLD = meta["legit_median"], meta["threshold"]

app = Flask(__name__)

# --------------------------------------------------------------- form definition
# kind: number | int | flag | choice ; group: main | advanced
FIELDS = [
    dict(name="amount", label="Amount (₹)", kind="number", group="main", min=1, max=10_000_000, step="any",
         help="Payment value in rupees."),
    dict(name="transaction_time_of_day", label="Hour of day (0-23)", kind="int", group="main", min=0, max=23,
         help="24-hour clock. 2 = 2 AM."),
    dict(name="transaction_amount_vs_sender_history", label="Amount vs. usual (×)", kind="number", group="main",
         min=0, max=1000, step="any", help="1 = normal for this sender; 5 = five times their usual amount."),
    dict(name="authentication_attempts", label="Authentication attempts", kind="int", group="main", min=1, max=10,
         help="PIN/OTP tries before this payment went through."),
    dict(name="failed_transaction_count", label="Recent failed payments", kind="int", group="main", min=0, max=20,
         help="Failed attempts just before this one."),
    dict(name="unusual_device_flag", label="Unusual device?", kind="flag", group="main", help="Not the sender's usual phone."),
    dict(name="unusual_ip_flag", label="Unusual IP / location?", kind="flag", group="main", help="Network or place the sender doesn't normally use."),
    dict(name="session_source", label="Session opened from", kind="choice", group="main", help="Directly in the app, or via a clicked link."),
    dict(name="pin_entry_method", label="PIN entry", kind="choice", group="main", help="Typed by hand or pasted."),
    dict(name="time_pressure_indicators", label="Time-pressure signals (0-5)", kind="int", group="advanced", min=0, max=5,
         help="Urgency cues, e.g. 'act now' messages."),
    dict(name="input_timing_consistency", label="Input timing consistency (0-1)", kind="number", group="advanced",
         min=0, max=1, step="0.01", help="Human typing is fairly consistent; scripted input differs."),
    dict(name="pin_entry_speed", label="PIN entry speed", kind="number", group="advanced", min=0, max=10, step="0.01",
         help="Relative speed; very low = suspiciously fast."),
    dict(name="transaction_velocity", label="Transaction velocity", kind="number", group="advanced", min=0, max=50, step="any",
         help="Payments in a short window."),
    dict(name="otp_request_frequency", label="OTP requests", kind="int", group="advanced", min=0, max=20,
         help="OTPs requested recently."),
    dict(name="session_duration", label="Session duration (s)", kind="number", group="advanced", min=0, max=5000, step="any"),
    dict(name="geographic_disparity", label="Geographic disparity (km)", kind="number", group="advanced", min=0, max=25000,
         step="any", help="Distance between expected and actual location."),
]
for f in FIELDS:
    if f["kind"] == "choice":
        f["options"] = meta["categories"][f["name"]]
        f["default"] = f["options"][0]
    elif f["kind"] in ("int", "flag"):
        f["default"] = int(round(MEDIAN[f["name"]]))
    else:
        f["default"] = round(MEDIAN[f["name"]], 4)

PRESETS = {
    "typical": {f["name"]: f["default"] for f in FIELDS},
    "suspicious": {
        **{f["name"]: f["default"] for f in FIELDS},
        "amount": 95000, "transaction_time_of_day": 2, "transaction_amount_vs_sender_history": 8,
        "authentication_attempts": 4, "failed_transaction_count": 2, "unusual_device_flag": 1,
        "unusual_ip_flag": 1, "session_source": "link", "pin_entry_method": "pasted",
        "time_pressure_indicators": 3,
    },
}


# ------------------------------------------------------------------- logic
def parse(form) -> dict:
    """Validate raw input -> clean dict. Raises ValueError with a friendly message."""
    values = {}
    for f in FIELDS:
        raw = form.get(f["name"], "")
        raw = str(raw).strip()
        if raw == "":
            values[f["name"]] = f["default"]
            continue
        if f["kind"] == "choice":
            if raw not in f["options"]:
                raise ValueError(f"'{f['label']}' must be one of {f['options']}.")
            values[f["name"]] = raw
            continue
        try:
            num = float(raw)
        except ValueError:
            raise ValueError(f"'{f['label']}' must be a number.") from None
        if not math.isfinite(num):
            raise ValueError(f"'{f['label']}' must be a finite number.")
        if f["kind"] == "flag":
            if num not in (0, 1):
                raise ValueError(f"'{f['label']}' must be Yes or No.")
        elif not (f["min"] <= num <= f["max"]):
            raise ValueError(f"'{f['label']}' must be between {f['min']} and {f['max']}.")
        values[f["name"]] = int(num) if f["kind"] in ("int", "flag") else num
    return values


def score(values: dict) -> float:
    row = pd.DataFrame([values])[NUMERIC + CATEGORICAL]
    return float(model.predict_proba(row)[0, 1])


def drivers(values: dict, base_p: float, top: int = 3):
    """Counterfactual: how much would the score drop if this ONE input were typical?"""
    out = []
    for f in FIELDS:
        n = f["name"]
        typical = f["default"]
        if values[n] == typical:
            continue
        alt = dict(values)
        alt[n] = typical
        drop = base_p - score(alt)
        if drop >= 0.02:
            out.append((f["label"], drop))
    return sorted(out, key=lambda t: -t[1])[:top]


def assess(values: dict) -> dict:
    p = score(values)
    band = "high" if p >= THRESHOLD else ("medium" if p >= 0.2 else "low")
    return {
        "probability": p,
        "percent": round(p * 100, 1),
        "is_fraud": p >= THRESHOLD,
        "band": band,
        "drivers": [(label, round(d * 100)) for label, d in drivers(values, p)] if p >= 0.2 else [],
    }


# ------------------------------------------------------------------- routes
@app.route("/", methods=["GET", "POST"])
def index():
    result, error, values = None, None, {f["name"]: f["default"] for f in FIELDS}
    if request.method == "POST":
        try:
            values = parse(request.form)
            result = assess(values)
        except ValueError as e:
            error = str(e)
            values = {f["name"]: request.form.get(f["name"], f["default"]) for f in FIELDS}
    return render_template("index.html", fields=FIELDS, values=values, result=result, error=error,
                           meta=meta, presets=PRESETS)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(silent=True) or {}
    try:
        values = parse({k: v for k, v in payload.items()})
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(assess(values))


@app.route("/health")
def health():
    return jsonify(status="ok", model=meta["model_name"], metrics=meta["test_metrics"])


if __name__ == "__main__":
    import os
    import socket

    def is_port_in_use(port_num: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port_num)) == 0

    target_port = int(os.environ.get("PORT", 5000))
    if is_port_in_use(target_port):
        print(f"⚠️  Port {target_port} is already in use (e.g. macOS AirPlay Receiver on port 5000).")
        target_port = 5001
        print(f"👉 Switching automatically to port {target_port}...")

    print(f"\n=======================================================")
    print(f"  🛡️ PaySafe India — UPI Fraud Risk Engine Running")
    print(f"  🌐 Access Web App at: http://127.0.0.1:{target_port}")
    print(f"  📡 API Healthcheck at: http://127.0.0.1:{target_port}/health")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=target_port, debug=False)

