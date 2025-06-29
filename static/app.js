document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("userInput");
    const sendBtn = document.querySelector(".send_button");
    const voiceBtn = document.querySelector(".mic_button");
    const chatMessages = document.getElementById("chat-messages");

    // === Add message to chat with avatar
    function addMessage(sender, text) {
        const row = document.createElement("div");
        row.className = `message__row ${sender === "User" ? "user" : "bot"}`;

        const avatar = document.createElement("img");
        avatar.className = "message__avatar";
        avatar.src = sender === "User"
            ? "static/images/user-avatar.png"
            : "static/images/bot-avatar.png";

        const bubble = document.createElement("div");
        bubble.className = `message__bubble ${sender === "User" ? "user" : "bot"}`;
        bubble.innerText = text;

        row.appendChild(avatar);
        row.appendChild(bubble);
        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // === Handle sending messages
    function sendMessage() {
        const message = inputField.value.trim();
        if (!message) return;

        addMessage("User", message);
        inputField.value = "";

        fetch("/predict", {
            method: "POST",
            body: JSON.stringify({ message }),
            headers: { "Content-Type": "application/json" }
        })
        .then(res => res.json())
        .then(data => {
            addMessage("Bot", data.answer || "Sorry, I couldn't process that.");
        })
        .catch(() => {
            addMessage("Bot", "Oops! Something went wrong.");
        });
    }

    // === Voice recognition support
    function startVoiceRecognition() {
        try {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "en-US";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
    
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                inputField.value = transcript;
            };
    
            recognition.onerror = (event) => {
                if (event.error === "no-speech") {
                    console.warn("🟡 No speech detected. Please try again.");
                    alert("No speech detected. Please try speaking again.");
                } else {
                    alert("Voice recognition error: " + event.error);
                }
            };
    
            recognition.onspeechend = () => {
                recognition.stop();
            };
    
            recognition.start();
        } catch (err) {
            alert("Speech recognition not supported.");
        }
    }   
   

    // === Event Listeners
    sendBtn.addEventListener("click", sendMessage);
    voiceBtn.addEventListener("click", startVoiceRecognition);

    inputField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});