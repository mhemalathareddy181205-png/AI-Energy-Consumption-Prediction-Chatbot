import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

data = pd.read_csv(
    "energy_forecast_data.csv"
)

X = data[
    [
        "income",
        "units",
        "fans",
        "lights",
        "tv_hours",
        "ac_hours",
        "wm_hours"
    ]
]

y = data["next_month_bill"]

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

joblib.dump(
    model,
    "bill_forecast_model.pkl"
)

print(
    "Forecast model saved successfully!"
)