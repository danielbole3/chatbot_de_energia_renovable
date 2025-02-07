document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById("messages");
    const inputField = document.getElementById("userInput");
    const sendButton = document.getElementById("sendMessageButton");
    let userName = null;
    let isMenuActive = false;

    function displayBotResponse(text) {
        console.log("Mostrando respuesta del chatbot:", text); // Verifica el contenido del mensaje
        const botMessage = document.createElement("p");
        botMessage.textContent = "Chatbot: " + text;
        messagesDiv.appendChild(botMessage);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Asegura que el scroll esté al final
    }

    function displayMainMenu() {
        console.log("Ejecutando displayMainMenu"); // Para confirmar que se ejecuta
        isMenuActive = true;
        displayBotResponse(
            "Por favor selecciona una opción:\n" +
            "1. Calcular ahorro.\n" +
            "2. Preguntas frecuentes sobre energía solar.\n" +
            "3. Hablar directamente con el chatbot."
        );
    }

    async function handleMenuSelection(option) {
        const normalizedOption = option.toLowerCase().trim();

        if (normalizedOption === "1" || normalizedOption.includes("calcular ahorro")) {
            await calculateSavings();
        } else if (normalizedOption === "2" || normalizedOption.includes("preguntas frecuentes")) {
            displayBotResponse(
                "Aquí tienes algunas preguntas frecuentes:\n" +
                "- ¿Cuánto duran los paneles solares?\n" +
                "- ¿Qué incentivos existen para paneles solares en Colombia?\n" +
                "- ¿Cómo afecta el clima a la producción de energía solar?"
            );
            displayMainMenu();
        } else if (normalizedOption === "3" || normalizedOption.includes("hablar directamente")) {
            isMenuActive = false; // Cambia a modo chat libre
            displayBotResponse("Perfecto, escribe tu pregunta y trataré de ayudarte.");
        } else {
            displayBotResponse("Opción no válida. Por favor selecciona 1, 2 o 3.");
            displayMainMenu();
        }
    }

    async function calculateSavings() {
        try {
            const department = prompt("Ingrese el departamento:");
            const monthlyConsumption = parseFloat(prompt("Ingrese su consumo mensual en kWh:"));
            const pricePerKwh = parseFloat(prompt("Ingrese el precio por kWh en COP:"));
            const annualMaintenanceCost = parseFloat(prompt("Ingrese el costo anual de mantenimiento en COP:"));
    
            if (!department || isNaN(monthlyConsumption) || isNaN(pricePerKwh) || isNaN(annualMaintenanceCost)) {
                displayBotResponse("Por favor, ingrese valores válidos para calcular el ahorro.");
                return;
            }
    
            const response = await fetch("/calculate_savings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    department: department,
                    monthly_consumption_kwh: monthlyConsumption,
                    price_per_kwh: pricePerKwh,
                }),
            });
    
            if (!response.ok) {
                displayBotResponse("No se pudo calcular el ahorro. Verifique los datos ingresados.");
                return;
            }
    
            const data = await response.json();
            const annualSavings = parseFloat(data.message.match(/([\d,.]+) COP al año/)[1].replace(/,/g, '')); // Extraer el valor del ahorro anual
    
            // Cálculos adicionales
            const savingsAfterMaintenance = annualSavings - annualMaintenanceCost; // Ahorro anual neto
            const savingsIn3Years = savingsAfterMaintenance * 3;
            const savingsIn15Years = savingsAfterMaintenance * 15;
    
            // Mostrar resultados
            displayBotResponse(`
                En ${department}, con un consumo mensual de ${monthlyConsumption} kWh y un precio de ${pricePerKwh} COP por kWh:
                - Ahorro neto anual (después del mantenimiento): ${savingsAfterMaintenance.toLocaleString()} COP.
                - Ahorro proyectado en 3 años: ${savingsIn3Years.toLocaleString()} COP.
                - Ahorro proyectado en 15 años (vida útil): ${savingsIn15Years.toLocaleString()} COP.
            `);
    
            displayMainMenu();
        } catch (error) {
            displayBotResponse("Hubo un error de conexión. Intente nuevamente.");
        }
    }
        window.sendMessage = async function () {
        console.log("sendMessage se ejecutó correctamente.");
        const message = inputField.value.trim();
        if (!message) return;

        const userMessage = document.createElement("p");
        userMessage.textContent = "Tú: " + message;
        messagesDiv.appendChild(userMessage);

        try {
            if (!userName) {
                userName = message; // Guardar el nombre del usuario
                const response = await fetch("/set_name", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: userName }),
                });
                const data = await response.json();
                console.log("Respuesta del servidor:", data); // Mostrar la respuesta del servidor
                displayBotResponse(data.message);
                displayMainMenu(); // Llamar al menú principal después de recibir el nombre
                console.log("displayMainMenu ejecutado."); // Confirmar que la función se ejecuta
                inputField.value = "";
                return;
            }

            if (isMenuActive) {
                await handleMenuSelection(message);
            } else {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: message }),
                });
                const data = await response.json();
                displayBotResponse(data.response || "Lo siento, no entiendo la pregunta.");
            }
        } catch (error) {
            displayBotResponse("Hubo un error de conexión.");
        }

        inputField.value = "";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    sendButton.addEventListener("click", sendMessage);

    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    displayBotResponse("Hola! Soy el Chatbot de Energías Renovables. ¿Cuál es tu nombre?");
    displayMainMenu();
});
