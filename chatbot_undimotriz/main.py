from fastapi import FastAPI
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

# Descargar recursos de NLTK (solo la primera vez)
nltk.download("punkt")
nltk.download("wordnet")

# Configurar FastAPI con Swagger personalizado
app = FastAPI(
    title="Chatbot de Energía 🌍⚡",
    description="Un chatbot para consultar datos de energía renovable y fósil en diferentes países y años.",
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

# ⚡ Montar archivos estáticos (por si los necesitamos más tarde)
app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi.responses import HTMLResponse

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
            .swagger-ui .topbar {
                background-color: #4CAF50 !important;
            }
            .swagger-ui .info h1 {
                color: white !important;
            }
            .swagger-ui .info p {
                color: white !important;
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
    """
    Convierte un valor numérico de energía a la unidad más adecuada (kW, MW o TWh).
    """
    if pd.isna(valor) or valor == "Dato no disponible":
        return "Dato no disponible"
    
    try:
        valor = float(valor)  # Intentar convertir a número
    except ValueError:
        return "Dato no disponible"  # Si falla la conversión, devolver mensaje

    if valor < 1:  
        return f"{valor * 1_000_000} kW"  # Convertir a kilovatios
    elif valor < 1_000:
        return f"{valor * 1_000} MW"  # Convertir a megavatios
    else:
        return f"{valor} TWh"  # Mantener en Teravatios


@app.get("/")
def read_root():
    return {"message": "Bienvenido al chatbot de energía mundial"}

@app.get("/chatbot")
def chatbot(query: str, country: str = "World", year: int = 2022):
    """
    Chatbot que responde consultas sobre energía en el mundo.
    Se puede filtrar por país y año.
    """
    # Tokenizar la consulta del usuario
    palabras_clave = word_tokenize(query.lower())

    # Buscar sinónimos para mejorar la búsqueda
    sinonimos = set()
    for palabra in palabras_clave:
        for syn in wordnet.synsets(palabra):
            for lema in syn.lemmas():
                sinonimos.add(lema.name().lower())

    # Recargar el dataset en cada consulta
    df = pd.read_csv(DATASET_FILE)  
    df_filtrado = df[(df["country"].str.lower() == country.lower()) & (df["year"] == year)]

    if df_filtrado.empty:
        return {"respuesta": f"No se encontraron datos para {country} en {year}."}

    # Buscar qué tipo de energía se menciona en la consulta
    resultados = {}
    for col, descripciones in columnas_interes.items():
        if isinstance(descripciones, list):  # Si hay sinónimos en la lista
            if any(s in " ".join(descripciones).lower() for s in sinonimos):
                valor = df_filtrado[col].values[0] if not df_filtrado[col].isna().all() else "Dato no disponible"
                resultados[descripciones[0]] = formatear_energia(valor)  # ✅ Mostrar solo la descripción principal
        else:  # Si es una sola descripción
            if any(s in col.lower() for s in sinonimos):
                valor = df_filtrado[col].values[0] if not df_filtrado[col].isna().all() else "Dato no disponible"
                resultados[descripciones] = formatear_energia(valor)

    if resultados:
        return {"respuesta": f"Datos energéticos para {country} en {year}:", "resultados": resultados}
    else:
        return {"respuesta": "No entendí la pregunta. Prueba preguntando sobre generación o consumo de energía."}

@app.post("/agregar_dato")
def agregar_dato(country: str, year: int, solar: float = 0, wind: float = 0, 
                 hydro: float = 0, wave: float = 0):
    """
    Agrega o actualiza datos de energía en el dataset.
    Ahora incluye energía undimotriz (wave_energy).
    """
    df = pd.read_csv(DATASET_FILE)

    # Verificar si ya existe el país y año en el dataset
    mask = (df["country"] == country) & (df["year"] == year)

    if mask.any():
        # Si ya existe, actualizar los datos
        df.loc[mask, "solar_electricity"] = solar
        df.loc[mask, "wind_electricity"] = wind
        df.loc[mask, "hydro_electricity"] = hydro
        df.loc[mask, "wave_energy"] = wave  # Nueva columna para energía undimotriz
    else:
        # Si no existe, agregar un nuevo registro
        nuevo_dato = pd.DataFrame([{
            "country": country,
            "year": year,
            "solar_electricity": solar,
            "wind_electricity": wind,
            "hydro_electricity": hydro,
            "wave_energy": wave  # Nueva columna
        }])
        df = pd.concat([df, nuevo_dato], ignore_index=True)

    df.to_csv(DATASET_FILE, index=False)
    
    return {"message": "✅ Dato agregado o actualizado correctamente"}
