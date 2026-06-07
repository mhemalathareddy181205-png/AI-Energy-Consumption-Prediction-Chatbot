from flask import Flask, render_template, request, jsonify
import joblib
import sqlite3

# Load models
intent_model = joblib.load("intent_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")
power_model = joblib.load("power_consumption_model.pkl")

# Create Flask app
app = Flask(__name__)

# Intent detection
def detect_intent(message):

    vector = vectorizer.transform([message])

    intent = intent_model.predict(vector)[0]

    return intent


# Sample prediction for chatbot
def predict_sample_power():

    sample = [[
        0.1,    # Global_reactive_power
        240,    # Voltage
        5,      # Global_intensity
        0,      # Sub_metering_1
        1,      # Sub_metering_2
        10,     # Sub_metering_3
        12,     # Hour
        15,     # Day
        6,      # Month
        2       # Weekday
    ]]

    prediction = power_model.predict(sample)

    return round(prediction[0], 3)


# Home Page
@app.route("/")
def home():

    return render_template("index.html")


# Chat API
@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    intent = detect_intent(user_message)

    print("User:", user_message)
    print("Intent:", intent)

    if intent == "greeting":

        response = "Hello! I am your Energy Assistant."

    elif intent == "thanks":

        response = "You're welcome!"

    elif intent == "goodbye":

        response = "Goodbye! Have a great day."

    elif intent == "capabilities":

        response = (
            "I can help with power prediction, energy saving tips, FAQs, and household power consumption analysis."
        )

    elif intent == "power_saving":

        response = (
            "To save electricity: use LED bulbs, switch off unused appliances, use energy-efficient devices, and avoid standby power consumption."
        )

    elif intent == "how_are_you":

        response = (
            "I'm doing great! Thanks for asking. How can I help you with energy consumption today?"
        )

    elif intent == "prediction":

        predicted_value = predict_sample_power()

        response = (
            f"Predicted Power Consumption: {predicted_value} kW"
        )

    else:

        response = "Sorry, I didn't understand that."

    # Save chat history
    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats
        (user_message, bot_response)
        VALUES (?, ?)
        """,
        (user_message, response)
    )

    conn.commit()

    conn.close()

    return jsonify({
        "response": response
    })


# Prediction Route
@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    features = [[

        float(data["reactive_power"]),
        float(data["voltage"]),
        float(data["intensity"]),
        float(data["sub1"]),
        float(data["sub2"]),
        float(data["sub3"]),
        float(data["hour"]),
        float(data["day"]),
        float(data["month"]),
        float(data["weekday"])

    ]]

    prediction = power_model.predict(features)[0]

    return jsonify({
        "prediction": round(prediction, 3)
    })


# Chat History Page
@app.route("/history")
def history():

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM chats
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        chats=rows
    )

import os

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )