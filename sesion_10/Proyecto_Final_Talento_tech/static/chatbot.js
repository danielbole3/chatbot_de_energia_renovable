document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById("messages");
    const inputField = document.getElementById("userInput");
    let userName = null;

    // Mostrar respuesta del chatbot en el cuadro de mensajes
    function displayBotResponse(text) {
        const botMessage = document.createElement("p");
        botMessage.textContent = "Chatbot: " + text;
        messagesDiv.appendChild(botMessage);
    }

    // Función para calcular ahorro anual
    async function calculateSavings() {
        try {
            const department = prompt("Ingrese el departamento:");
            const monthlyConsumption = parseFloat(prompt("Ingrese su consumo mensual en kWh:"));
            const pricePerKwh = parseFloat(prompt("Ingrese el precio por kWh en COP:"));
    
            if (!department || isNaN(monthlyConsumption) || isNaN(pricePerKwh)) {
                displayBotResponse("Por favor, ingrese valores válidos para calcular el ahorro.");
                return;
            }
    
            const response = await fetch("/calculate_savings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    department: department,
                    monthly_consumption_kwh: monthlyConsumption,
                    price_per_kwh: pricePerKwh
                })
            });
    
            if (!response.ok) {
                displayBotResponse("No se pudo calcular el ahorro. Verifique los datos ingresados.");
                return;
            }
    
            const data = await response.json();
            displayBotResponse(data.message || "No se pudo calcular el ahorro.");
        } catch (error) {
            displayBotResponse("Hubo un error de conexión. Intente nuevamente.");
        }
    }
    
    async function sendMessage() {
        const message = inputField.value.trim();
        if (!message) return;
    
        const userMessage = document.createElement("p");
        userMessage.textContent = "Tú: " + message;
        messagesDiv.appendChild(userMessage);
    
        try {
            if (message.toLowerCase() === "calcular ahorro") {
                await calculateSavings();
                return;
            }
    
            if (!userName) {
                const response = await fetch("/set_name", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: message })
                });
                const data = await response.json();
                userName = message;
                displayBotResponse(data.message);
            } else {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: message })
                });
                const data = await response.json();
                displayBotResponse(data.response || "Lo siento, no entiendo la pregunta.");
            }
        } catch (error) {
            displayBotResponse("Hubo un error de conexión.");
        }
    
        inputField.value = "";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    

    // Función para enviar mensajes al backend
    async function sendMessage() {
        const message = inputField.value.trim();
        if (!message) return;

        const userMessage = document.createElement("p");
        userMessage.textContent = "Tú: " + message;
        messagesDiv.appendChild(userMessage);

        try {
            if (message.toLowerCase() === "calcular ahorro") {
                await calculateSavings();
                return;
            }

            if (!userName) {
                const response = await fetch("/set_name", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: message })
                });

                const data = await response.json();
                userName = message;
                displayBotResponse(data.message);
            } else {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: message })
                });

                const data = await response.json();
                displayBotResponse(data.response || "Lo siento, no entiendo la pregunta.");
            }
        } catch (error) {
            displayBotResponse("Hubo un error de conexión. Intente nuevamente.");
        }

        inputField.value = "";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Eventos para botón de enviar y tecla Enter
    document.querySelector("button").addEventListener("click", sendMessage);
    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Mensaje de saludo inicial
    displayBotResponse("Hola! Soy el Chatbot de Energías Renovables. ¿Cuál es tu nombre?");
});

document.addEventListener("DOMContentLoaded", function () {
    function updateDateTime() {
        const datetimeDiv = document.getElementById("datetime");

        if (!datetimeDiv) {
            console.error("Elemento #datetime no encontrado en el HTML.");
            return;
        }

        // Actualiza la fecha y hora
        const now = new Date();
        const date = now.toLocaleDateString();
        const time = now.toLocaleTimeString();

        // Datos simulados de temperatura
        const temperature = 25; // Temperatura simulada en °C
        const feelsLike = 27; // Sensación térmica simulada en °C

        datetimeDiv.innerHTML = `
            Fecha: ${date} - Hora: ${time} <br> 
            Temp: ${temperature}°C | Sensación térmica: ${feelsLike}°C
        `;
    }

    // Actualiza los datos cada minuto
    setInterval(updateDateTime, 60000); // Actualiza cada minuto
    updateDateTime(); // Llama una vez al cargar
});
