from fastapi import FastAPI
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
import re

# Descargar recursos de NLTK (solo la primera vez)
nltk.download("punkt")
nltk.download("wordnet")

# Configurar FastAPI con Swagger personalizado
app = FastAPI(
    title="greenbot 🌍⚡",
    description="Un chatbot para predecir el consumo de energía en el mundo.",
    version="1.0",
    contact={
        "name": "Daniel Alejandro",
        "email": "danicalderon7089@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Montar archivos estáticos (por si los necesitamos más tarde)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta para la documentación Swagger personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot de Energía - API Docs</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.0.0/swagger-ui.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.0.0/swagger-ui-bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.0.0/swagger-ui-standalone-preset.min.js"></script>
        <style>
            body {
                background-color: #1e1e1e !important;
                color: white !important;
            }
            .swagger-ui {
                background-color: #1e1e1e !important;
            }
            /* Centrar todo el contenido del Swagger UI */
            .swagger-ui .topbar {
                display: flex;
                justify-content: center;
                background-color:rgb(247, 7, 7) !important;
            }
            .swagger-ui .topbar .swagger-ui-wrap {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .swagger-ui .info h1 {
                color: white !important;
                text-align: center !important;  /* Centra el título */
                font-size: 30px !important;
                margin-top: 20px;  /* Para darle algo de espacio */
            }
            .swagger-ui .info p {
                color: white !important;
                text-align: center !important;  /* Centra la descripción */
                font-size: 16px !important;
            }
            .swagger-ui .btn {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            .swagger-ui input,
            .swagger-ui textarea {
                background-color: #333 !important;
                color: white !important;
                border: 1px solid #4CAF50 !important;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
                    layout: "StandaloneLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Cargar el dataset de energía mundial
DATASET_FILE = "World Energy Consumption.csv"
USER_DATA_FILE = "user_data.csv"  # Archivo donde almacenaremos los datos personales

# Columnas de interés para el chatbot con sinónimos
columnas_interes = {
    "electricity_generation": "Generación de electricidad (TWh)",
    "primary_energy_consumption": "Consumo total de energía (TWh)",
    "renewables_electricity": "Electricidad renovable (TWh)",
    "solar_electricity": "Electricidad solar (TWh)",
    "wind_electricity": "Electricidad eólica (TWh)",
    "hydro_electricity": "Electricidad hidroeléctrica (TWh)",
    "coal_electricity": "Electricidad por carbón (TWh)",
    "oil_electricity": "Electricidad por petróleo (TWh)",
    "gas_electricity": "Electricidad por gas (TWh)",
    "wave_energy": ["Energía undimotriz (TWh)", "olas", "mar", "energía de las olas", "mareomotriz"],  # Nueva columna
}

# ✅ Función para convertir energía a la unidad correcta
def formatear_energia(valor):
    if isinstance(valor, list) or pd.isna(valor) or valor == "Dato no disponible":
        return "Dato no disponible"
    
    try:
        valor = float(valor)  # Intentar convertir a float
    except ValueError:
        return "Dato no disponible"

    if valor < 1:
        return f"{valor * 1_000_000} kW"
    elif valor < 1_000:
        return f"{valor * 1_000} MW"
    else:
        return f"{valor} TWh"

# Entrenamiento de los modelos de predicción (solo se realiza una vez)
df = pd.read_csv(DATASET_FILE)
df = df[['year', 'country', 'primary_energy_consumption', 'electricity_generation']]
df_filtrado = df[df['country'].str.lower() == 'world']
df_filtrado = df_filtrado.dropna()

# Entrenar el modelo de consumo energético
X = df_filtrado[['year']]
y_consumo = df_filtrado['primary_energy_consumption']
X_train, X_test, y_train_consumo, y_test_consumo = train_test_split(X, y_consumo, test_size=0.2, random_state=42)
modelo_consumo = LinearRegression()
modelo_consumo.fit(X_train, y_train_consumo)

# Entrenar el modelo de generación energética
y_generacion = df_filtrado['electricity_generation']
X_train, X_test, y_train_generacion, y_test_generacion = train_test_split(X, y_generacion, test_size=0.2, random_state=42)
modelo_generacion = LinearRegression()
modelo_generacion.fit(X_train, y_train_generacion)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al chatbot de energía mundial"}

@app.get("/chatbot")
def chatbot(query: str, country: str = "World", year: int = 2022, futuro_año: int = None):
    if not futuro_año:
        futuro_año = 2030

    # Tokenizar la consulta
    palabras_clave = word_tokenize(query.lower())

    # Cargar el dataset
    df = pd.read_csv(DATASET_FILE)
    df_filtrado = df[(df["country"].str.lower() == country.lower()) & (df["year"] == year)]

    if df_filtrado.empty:
        return {"respuesta": f"No se encontraron datos para {country} en {year}."}

    # Predicción para el futuro año
    if "predicción" in query or "futuro" in query:
        prediccion_consumo = modelo_consumo.predict([[futuro_año]])
        prediccion_generacion = modelo_generacion.predict([[futuro_año]])

        return {
            "respuesta": f"Predicciones energéticas para el año {futuro_año}:",
            "consumo_predicho": f"{prediccion_consumo[0]:.2f} TWh",
            "generacion_predicha": f"{prediccion_generacion[0]:.2f} TWh"
        }

    # Responder con los datos actuales
    resultados = {}
    for col, descripcion in columnas_interes.items():
        valor = df_filtrado[col].values[0] if not df_filtrado[col].isna().all() else "Dato no disponible"
        # Comprobar si 'valor' es una lista
        if isinstance(valor, list):
            valor = valor[0]  # Obtener el primer valor de la lista si es necesario

        # Comprobar si 'descripcion' es una lista
        if isinstance(descripcion, list):
            descripcion = descripcion[0]  # Obtener el primer valor de la lista

        resultados[descripcion] = formatear_energia(valor)

    if resultados:
        return {"respuesta": f"Datos energéticos para {country} en {year}:", "resultados": resultados}
    else:
        return {"respuesta": "No entendí la pregunta. Prueba preguntando sobre generación o consumo de energía."}


@app.post("/agregar_dato")
def agregar_dato(country: str, year: int, solar: float = 0, wind: float = 0, 
                 hydro: float = 0, wave: float = 0):
    df = pd.read_csv(DATASET_FILE)

    # Verificar si ya existe el país y año en el archivo
    if df[(df["country"] == country) & (df["year"] == year)].empty:
        # Si no existe, agregar un nuevo dato
        df = df.append({
            "country": country,
            "year": year,
            "solar_electricity": solar,
            "wind_electricity": wind,
            "hydro_electricity": hydro,
            "wave_energy": wave,
        }, ignore_index=True)

        # Guardar en el archivo
        df.to_csv(DATASET_FILE, index=False)

        return {"message": "Datos agregados exitosamente"}
    else:
        return {"message": "Los datos para este país y año ya existen"}

# Iniciar el servidor con uvicorn en lugar de fastapi


@app.post("/agregar_dato_personal")
def agregar_dato_personal(consumo_mensual_kWh: float, user_id: str):
    """
    Agrega o actualiza los datos de consumo personal al dataset.
    """
    # Intentar cargar el archivo de datos del usuario
    try:
        df_user = pd.read_csv("user_data.csv")
        print("Datos cargados correctamente desde 'user_data.csv'.")
    except FileNotFoundError:
        df_user = pd.DataFrame(columns=["user_id", "consumo_mensual_kWh"])
        print("Archivo 'user_data.csv' no encontrado, creando nuevo DataFrame.")
    
    # Crear el nuevo dato
    nuevo_dato_personal = pd.DataFrame([{
        "user_id": user_id,
        "consumo_mensual_kWh": consumo_mensual_kWh
    }])

    # Concatenar el nuevo dato al DataFrame existente
    df_user = pd.concat([df_user, nuevo_dato_personal], ignore_index=True)

    # Guardar el DataFrame actualizado
    df_user.to_csv("user_data.csv", index=False)
    print(f"Dato agregado para el usuario {user_id}: {nuevo_dato_personal}")
    
    return {"message": "✅ Dato personal agregado correctamente"}



@app.get("/prediccion_consumo_personal")
def prediccion_consumo_personal(user_id: str):
    """
    Predice el consumo anual y futuro basado en los datos personales guardados.
    """
    try:
        df_user = pd.read_csv(USER_DATA_FILE)
        print("Datos personales cargados correctamente.")
    except FileNotFoundError:
        return {"respuesta": "El archivo de datos personales no se encuentra."}

    user_data = df_user[df_user["user_id"] == user_id]

    if user_data.empty:
        return {"respuesta": "No se encontraron datos personales para este usuario."}

    # Obtener el consumo mensual y calcular el consumo anual
    consumo_mensual_kWh = user_data["consumo_mensual_kWh"].values[0]
    consumo_anual_kWh = consumo_mensual_kWh * 12

    # Predicción de consumo futuro utilizando el modelo global
    consumo_predicho_futuro = modelo_consumo.predict([[2022]])[0]

    return {
        "respuesta": f"Predicción de Consumo Personal para {user_id}",
        "consumo_anual_estimado": f"{consumo_anual_kWh:.2f} kWh",
        "consumo_predicho_futuro": f"{consumo_predicho_futuro:.2f} TWh"
    }

import re

@app.get("/chatbot_personal")
def chatbot_personal(query: str, user_id: str):
    """
    Un chatbot que responde preguntas sobre el consumo personal basándose únicamente en los datos de user_data.csv.
    """
    try:
        # Cargar los datos personales
        df_user = pd.read_csv(USER_DATA_FILE)
    except FileNotFoundError:
        return {"respuesta": "No se encontró el archivo de datos personales."}

    # Filtrar los datos para el usuario específico
    user_data = df_user[df_user["user_id"] == user_id]

    if user_data.empty:
        return {"respuesta": "No se encontraron datos personales para este usuario."}

    # Obtener el consumo mensual (y convertirlo a anual si es necesario)
    consumo_mensual_kWh = user_data["consumo_mensual_kWh"].values[0]
    consumo_anual_kWh = consumo_mensual_kWh * 12

    # Convertir consumo mensual a consumo por segundo, minuto y hora
    segundos_en_un_mes = 30 * 24 * 60 * 60  # 30 días * 24 horas * 60 minutos * 60 segundos
    minutos_en_un_mes = segundos_en_un_mes / 60
    horas_en_un_mes = minutos_en_un_mes / 60

    consumo_por_segundo = consumo_mensual_kWh / segundos_en_un_mes
    consumo_por_minuto = consumo_mensual_kWh / minutos_en_un_mes
    consumo_por_hora = consumo_mensual_kWh / horas_en_un_mes

    # Procesar la consulta
    palabras_clave = word_tokenize(query.lower())

    # Buscar si hay una cantidad de tiempo mencionada en segundos, minutos u horas
    tiempo_match = re.search(r'(\d+)\s*(segundos?|minutos?|horas?)', query.lower())

    if tiempo_match:
        cantidad = int(tiempo_match.group(1))  # La cantidad (30, por ejemplo)
        unidad = tiempo_match.group(2)  # La unidad de tiempo (segundos, minutos, horas)

        if "segundo" in unidad:
            energia_consumida = consumo_por_segundo * cantidad
            return {
                "respuesta": f"El consumo estimado para {user_id} en {cantidad} segundos es: {energia_consumida:.8f} kWh"
            }

        elif "minuto" in unidad:
            energia_consumida = consumo_por_minuto * cantidad
            return {
                "respuesta": f"El consumo estimado para {user_id} en {cantidad} minutos es: {energia_consumida:.6f} kWh"
            }

        elif "hora" in unidad:
            energia_consumida = consumo_por_hora * cantidad
            return {
                "respuesta": f"El consumo estimado para {user_id} en {cantidad} horas es: {energia_consumida:.4f} kWh"
            }

    # Responder sobre el consumo mensual o anual
    palabras_clave = word_tokenize(query.lower())
    if "consumo" in palabras_clave and "anual" in palabras_clave:
        return {
            "respuesta": f"Consumo anual estimado para {user_id}: {consumo_anual_kWh:.2f} kWh"
        }

    if "mensual" in palabras_clave and "consumo" in palabras_clave:
        return {
            "respuesta": f"Consumo mensual registrado para {user_id}: {consumo_mensual_kWh:.2f} kWh"
        }

    if "futuro" in palabras_clave or "predicción" in palabras_clave:
        return {
            "respuesta": "Este chatbot no tiene predicciones a futuro basadas solo en los datos personales."
        }

    return {"respuesta": "No entendí la pregunta. Puedes preguntar sobre tu consumo mensual, anual, por segundo, por minuto o por hora."}
