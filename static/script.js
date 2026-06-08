async function sendMessage() {

    let message =
        document.getElementById("message").value;

    let chatbox =
        document.getElementById("chatbox");

    if (message.trim() === "") {
        return;
    }

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

function calculateBill() {

    const income =
        parseFloat(
            document.getElementById("income").value
        );

    const tariff =
        parseFloat(
            document.getElementById("tariff").value
        );

    const previousReading =
        parseFloat(
            document.getElementById("previous_reading").value
        );

    const currentReading =
        parseFloat(
            document.getElementById("current_reading").value
        );

    const fans =
        parseInt(
            document.getElementById("fans").value
        );

    const lights =
        parseInt(
            document.getElementById("lights").value
        );

    const tvHours =
        parseFloat(
            document.getElementById("tv_hours").value
        );

    const acHours =
        parseFloat(
            document.getElementById("ac_hours").value
        );

    const wmHours =
        parseFloat(
            document.getElementById("wm_hours").value
        );

    const refrigerator =
        document.getElementById("refrigerator").value;

    fetch("/analyze", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            income: income,

            tariff: tariff,

            previous_reading:
                previousReading,

            current_reading:
                currentReading,

            fans: fans,

            lights: lights,

            tv_hours:
                tvHours,

            ac_hours:
                acHours,

            wm_hours:
                wmHours,

            refrigerator:
                refrigerator

        })

    })

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            document.getElementById(
                "predictionResult"
            ).innerHTML =
            `<p style="color:red;">
                ${data.error}
            </p>`;

            return;
        }

        document.getElementById(
            "predictionResult"
        ).innerHTML = `

        <h3>⚡ Energy Report</h3>

        <p>
        <b>Units Consumed:</b>
        ${data.units}
        </p>

        <p>
        <b>Estimated Bill:</b>
        ₹${data.bill}
        </p>

        <p>
        <b>Recommended Budget:</b>
        ₹${data.budget}
        </p>

        <p>
        <b>Status:</b>
        ${data.status}
        </p>

        <p>
        <b>Potential Savings:</b>
        ₹${data.saving_amount}
        </p>

        <p>
        <b>Possible Units Saved:</b>
        ${data.saving_units}
        </p>

        <p>
        <b>Predicted Next Month Bill:</b>
        ₹${data.next_month_bill}
        </p>

        <p>
        <b>Suggestions:</b>
        </p>

        <ul>
        ${data.suggestions}
        </ul>

        `;

    })

    .catch(error => {

        console.error(error);

        document.getElementById(
            "predictionResult"
        ).innerHTML =
        "<p>Error calculating bill.</p>";

    });

}