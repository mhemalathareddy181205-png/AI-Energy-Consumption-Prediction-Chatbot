import joblib

model = joblib.load("power_consumption_model.pkl")

print("Model loaded successfully")

try:
    print("Features:", model.feature_names_in_)
except:
    print("Feature names not available")