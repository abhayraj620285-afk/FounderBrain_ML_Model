from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = joblib.load("model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

@app.get("/")
def home():
    return {"message": "ML API is running 🚀"}

@app.post("/predict")
def predict(data: dict):

    try:
        # Convert input to array
        input_data = np.array([[
            data["revenue"],
            data["lastMonthRevenue"],
            data["monthlyExpenses"],
            data["cashReserve"],
            data["users"]
        ]])

        # Predict
        prediction = model.predict(input_data)
        probabilities = model.predict_proba(input_data)

        risk = label_encoder.inverse_transform(prediction)[0]
        confidence = float(max(probabilities[0]))
        return {
            "risk": risk,
            "confidence": confidence
        }

    except Exception as e:
        return {
            "error": str(e)
        }
    # uvicorn app:app --reload --port 8000
    