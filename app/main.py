from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import joblib
import pandas as pd
from pathlib import Path

app = FastAPI()

# =========================
# BASE DIRECTORY
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# STATIC + TEMPLATES
# =========================
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "app" / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "app" / "templates"
)

# =========================
# LOAD MODEL
# =========================
model = joblib.load(
    BASE_DIR / "models" / "churn_model.pkl"
)

feature_columns = joblib.load(
    BASE_DIR / "models" / "feature_columns.pkl"
)

# =========================
# INPUT SCHEMA
# =========================
class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

# =========================
# HOME PAGE
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

# =========================
# PREPROCESS FUNpython -m uvicorn app.main:app --reloadCTION
# =========================
def preprocess_input(data: CustomerData):

    input_dict = data.dict()

    binary_mapping = {
        "Yes": 1,
        "No": 0,
        "Male": 1,
        "Female": 0
    }

    binary_cols = [
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "PaperlessBilling"
    ]

    processed = {}

    # Numeric columns
    processed["SeniorCitizen"] = input_dict["SeniorCitizen"]
    processed["tenure"] = input_dict["tenure"]
    processed["MonthlyCharges"] = input_dict["MonthlyCharges"]
    processed["TotalCharges"] = input_dict["TotalCharges"]

    # Binary columns
    for col in binary_cols:
        processed[col] = binary_mapping[input_dict[col]]

    # DataFrame create
    input_df = pd.DataFrame([processed])

    # One-hot encoding columns
    multi_cols = [
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaymentMethod"
    ]

    for col in multi_cols:
        dummy_col = f"{col}_{input_dict[col]}"
        input_df[dummy_col] = 1

    # Missing columns add
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Same order as training
    input_df = input_df[feature_columns]

    return input_df

# =========================
# PREDICTION API
# =========================
@app.post("/predict")
def predict(data: CustomerData):

    input_df = preprocess_input(data)

    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0][1]

    result = "Churn" if prediction == 1 else "No Churn"

    return {
        "prediction": int(prediction),
        "result": result,
        "churn_probability": round(float(probability), 3)
    }