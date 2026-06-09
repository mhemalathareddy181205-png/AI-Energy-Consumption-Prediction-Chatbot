from flask import Flask, render_template, request, jsonify
import joblib
import sqlite3
import os

print("Loading intent model...")
intent_model = joblib.load("intent_model.pkl")

print("Loading vectorizer...")
vectorizer = joblib.load("vectorizer.pkl")

print("Loading forecast model...")
bill_forecast_model = joblib.load("bill_forecast_model.pkl")

print("All models loaded successfully!")


# Create Flask app
app = Flask(__name__)

# Store conversation state
user_sessions = {}

questions = [
    ("income", "What is your monthly income (₹)?"),
    ("tariff", "What is your electricity tariff (₹/unit)?"),
    ("previous_reading", "What is your previous meter reading?"),
    ("current_reading", "What is your current meter reading?"),
    ("fans", "How many fans do you have?"),
    ("lights", "How many lights do you have?"),
    ("tv_hours", "How many hours per day do you use the TV?"),
    ("ac_hours", "How many hours per day do you use the AC?"),
    ("wm_hours", "How many hours per week do you use the washing machine?"),
    ("refrigerator", "Do you have a refrigerator? (Yes/No)")
]



# Intent Detection
def detect_intent(message):

    vector = vectorizer.transform([message])

    intent = intent_model.predict(vector)[0]

    return intent


# Home Page
@app.route("/")
def home():

    return render_template("index.html")

def is_consumption_request(message):

    msg = message.lower()

    keywords = [
    "calculate consumption",
    "analyze consumption",
    "calculate bill",
    "electricity bill",
    "energy analysis"
    ]

    return any(
        keyword in msg
        for keyword in keywords
    )


# Chat API
@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]
    user_id = "default_user"

    # Start consumption analysis
    if is_consumption_request(user_message):

        user_sessions[user_id] = {
            "step": 0,
            "answers": {}
        }

        return jsonify({
            "response": questions[0][1]
        })

    # Continue conversation flow
    if user_id in user_sessions:

        session = user_sessions[user_id]

        step = session["step"]

        field_name = questions[step][0]

        session["answers"][field_name] = user_message

        session["step"] += 1

        # Ask next question
        if session["step"] < len(questions):

            return jsonify({
                "response": questions[session["step"]][1]
            })

        # All answers collected
        data = session["answers"]

        del user_sessions[user_id]

        try:

            income = float(data["income"])
            tariff = float(data["tariff"])
            previous_reading = float(data["previous_reading"])
            current_reading = float(data["current_reading"])
            fans = int(data["fans"])
            lights = int(data["lights"])
            tv_hours = float(data["tv_hours"])
            ac_hours = float(data["ac_hours"])
            wm_hours = float(data["wm_hours"])
            refrigerator = data["refrigerator"]

            if current_reading < previous_reading:

                return jsonify({
                    "response":
                    "Current reading must be greater than or equal to previous reading."
                })

            units = current_reading - previous_reading

            bill = units * tariff

            budget = income * 0.05

            status = (
                "✅ Within Budget"
                if bill <= budget
                else "⚠ Above Budget"
            )

            suggestions = []

            if ac_hours > 8:
                suggestions.append(
                    "Reduce AC usage by 1–2 hours per day."
                )

            if lights > 10:
                suggestions.append(
                    "Switch to LED bulbs."
                )

            if fans > 5:
                suggestions.append(
                    "Consider energy-efficient fans."
                )

            if refrigerator.lower() == "yes":
                suggestions.append(
                    "Keep refrigerator doors closed properly."
                )

            if wm_hours > 5:
                suggestions.append(
                    "Reduce washing machine usage where possible."
                )

            if bill > budget:
                suggestions.append(
                    "Your bill exceeds the recommended budget."
                )

            if not suggestions:
                suggestions.append(
                    "Great job! Your energy usage appears efficient."
                )

            forecast_features = [[
                income,
                units,
                fans,
                lights,
                tv_hours,
                ac_hours,
                wm_hours
            ]]

            next_month_bill = (
                bill_forecast_model.predict(
                    forecast_features
                )[0]
            )

            response = f"""
           📊 <b>Energy Analysis Result</b><br><br>
           ⚡ Units Consumed: {units:.2f}<br>
           💰 Current Bill: ₹{bill:.2f}<br>
           🎯 Recommended Budget: ₹{budget:.2f}<br>
           📈 Status: {status}<br>
           🔮 Forecast Next Month Bill: ₹{next_month_bill:.2f}<br><br>
           <b>Suggestions:</b><br>
           """ + "<br>".join(
               f"• {item}"
               for item in suggestions
               )

            response += """
            <br><br>
            <hr>
            💡 <b>Tip:</b> Type <b>'calculate consumption'</b>
            anytime to perform another analysis.
            """
            
            return jsonify({
                "response": response
                })
        except Exception as e:
            
            return jsonify({
                "response": f"Error processing analysis: {str(e)}"
                })
            
    # Normal chatbot flow
    intent = detect_intent(user_message)

    if intent == "greeting":

        response = (
            "Hello! I am your Energy Budget Assistant."
        )

    elif intent == "thanks":

        response = "You're welcome!"

    elif intent == "goodbye":

        response = (
            "Goodbye! Have a great day."
        )

    elif intent == "capabilities":

        response = (
            "I can analyze electricity usage, estimate bills, compare them with your budget, forecast next month's bill, and provide energy-saving recommendations."
        )

    elif intent == "power_saving":

        response = (
            "Use LED bulbs, switch off unused appliances, reduce AC usage, and avoid standby power consumption."
        )

    elif intent == "how_are_you":

        response = (
            "I'm doing great! How can I help you manage your electricity consumption today?"
        )

    elif intent == "prediction":

        response = (
            "Type 'calculate consumption' and I will ask the required details one by one."
        )

    else:

        response = (
            "Sorry, I didn't understand that."
        )

    conn = sqlite3.connect(
        "chat_history.db"
    )

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

   


# Energy Budget Analysis
@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.json

    income = float(data["income"])
    tariff = float(data["tariff"])

    previous_reading = float(
        data["previous_reading"]
    )

    current_reading = float(
        data["current_reading"]
    )

    fans = int(data["fans"])
    lights = int(data["lights"])

    tv_hours = float(
        data["tv_hours"]
    )

    ac_hours = float(
        data["ac_hours"]
    )

    wm_hours = float(
        data["wm_hours"]
    )

    refrigerator = data["refrigerator"]

    # Validation

    if current_reading < previous_reading:

        return jsonify({

            "error":
            "It looks like the readings were entered in reverse order. Current reading should be greater than or equal to previous reading."

            })


    # Units Consumed

    units = (
        current_reading -
        previous_reading
    )

    
    # Electricity Bill

    bill = units * tariff

    # Recommended Budget
    # 5% of Monthly Income

    budget = income * 0.05

    # Budget Status

    if bill <= budget:

        status = "✅ Within Budget"

    else:

        status = "⚠ Above Budget"

    # Suggestions

    suggestions = ""

    if ac_hours > 8:

        suggestions += (
            "<li>Reduce AC usage by 1-2 hours per day.</li>"
        )

    if lights > 10:

        suggestions += (
            "<li>Switch to LED bulbs to reduce electricity consumption.</li>"
        )

    if fans > 5:

        suggestions += (
            "<li>Consider energy-efficient fans.</li>"
        )

    if refrigerator.lower() == "yes":

        suggestions += (
            "<li>Keep refrigerator doors closed properly to reduce energy loss.</li>"
        )

    if wm_hours > 5:

        suggestions += (
            "<li>Reduce washing machine usage where possible.</li>"
        )

    if bill > budget:

        suggestions += (
            "<li>Your bill exceeds the recommended budget. Consider reducing appliance usage.</li>"
        )

    if suggestions == "":

        suggestions = (
            "<li>Great job! Your energy usage appears efficient.</li>"
        )

    # Estimated Savings

    ac_saving_units = ac_hours * 1.5
    tv_saving_units = tv_hours * 0.1
    wm_saving_units = wm_hours * 0.5

    total_saving_units = (
        ac_saving_units +
        tv_saving_units +
        wm_saving_units
    )

    estimated_saving_amount = (
        total_saving_units *
        tariff
    )
    # Next Month Bill Forecast

    forecast_features = [[
        
        income,
        units,
        fans,
        lights,
        tv_hours,
        ac_hours,
        wm_hours
        ]]

    next_month_bill = (
        bill_forecast_model
        .predict(
            forecast_features
            )[0]
            )

    return jsonify({

        "units": round(
            units,
            2
        ),

        "bill": round(
            bill,
            2
        ),

        "budget": round(
            budget,
            2
        ),

        "status": status,

        "suggestions": suggestions,

        "saving_units": round(
            total_saving_units,
            2
        ),

        "saving_amount": round(
            estimated_saving_amount,
            2
        ),
        "next_month_bill": round(
        next_month_bill,
        2
    )

    })


# Chat History
@app.route("/history")
def history():

    conn = sqlite3.connect(
        "chat_history.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM chats
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        chats=rows
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )