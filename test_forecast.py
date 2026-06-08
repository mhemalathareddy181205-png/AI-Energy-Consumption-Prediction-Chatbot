import joblib

model = joblib.load(
    "bill_forecast_model.pkl"
)

print("Forecast model loaded successfully!")