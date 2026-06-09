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