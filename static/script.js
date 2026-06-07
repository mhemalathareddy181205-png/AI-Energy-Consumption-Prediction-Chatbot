async function sendMessage() {

    let message =
        document.getElementById("message").value;

    if (message.trim() === "") {
        return;
    }

    let chatbox =
        document.getElementById("chatbox");

    chatbox.innerHTML +=
        `<div class="user">
            <b>You:</b> ${message}
        </div>`;

    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });

    const data = await response.json();

    chatbox.innerHTML +=
        `<div class="bot">
            <b>Bot:</b> ${data.response}
        </div>`;

    document.getElementById("message").value = "";

    chatbox.scrollTop =
        chatbox.scrollHeight;
}


document
.getElementById("message")
.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {

        sendMessage();

    }

});


function predictPower() {

    const datetime =
        document.getElementById("datetime").value;

    if (!datetime) {

        alert("Please select Date & Time");

        return;
    }

    const date =
        new Date(datetime);

    const hour =
        date.getHours();

    const day =
        date.getDate();

    const month =
        date.getMonth() + 1;

    const weekday =
        date.getDay();

    fetch("/predict", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            reactive_power:
            document.getElementById(
                "reactive_power"
            ).value,

            voltage:
            document.getElementById(
                "voltage"
            ).value,

            intensity:
            document.getElementById(
                "intensity"
            ).value,

            sub1:
            document.getElementById(
                "sub1"
            ).value,

            sub2:
            document.getElementById(
                "sub2"
            ).value,

            sub3:
            document.getElementById(
                "sub3"
            ).value,

            hour: hour,

            day: day,

            month: month,

            weekday: weekday

        })

    })

    .then(response => response.json())

    .then(data => {

        document.getElementById(
            "predictionResult"
        ).innerHTML =

        `<h3>
            Predicted Power Consumption:
            ${data.prediction} kW
        </h3>`;

    });

}


function calculateBudget() {

    const income =
        parseFloat(
            document.getElementById(
                "income"
            ).value
        );

    const rate =
        parseFloat(
            document.getElementById(
                "rate"
            ).value
        );

    if (!income || !rate) {

        alert(
            "Please enter Income and Electricity Rate"
        );

        return;
    }

    const predictionText =
        document.getElementById(
            "predictionResult"
        ).innerText;

    const match =
        predictionText.match(/[0-9.]+/);

    if (!match) {

        alert(
            "Please predict power consumption first."
        );

        return;
    }

    const power =
        parseFloat(match[0]);

    const estimatedBill =
        power * 30 * rate;

    const recommendedBudget =
        income * 0.05;

    let status = "";

    if (
        estimatedBill <=
        recommendedBudget
    ) {

        status =
            "✅ Within Budget";

    } else {

        status =
            "⚠ Above Recommended Budget";

    }

    document.getElementById(
        "budgetResult"
    ).innerHTML =

    `
    <h3>Budget Analysis</h3>

    <p>
    <b>Estimated Monthly Bill:</b>
    ₹${estimatedBill.toFixed(2)}
    </p>

    <p>
    <b>Recommended Electricity Budget:</b>
    ₹${recommendedBudget.toFixed(2)}
    </p>

    <p>
    <b>Status:</b>
    ${status}
    </p>
    `;
}