from fastapi import FastAPI, Request
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
import re

# Descargar recursos de NLTK (solo la primera vez)
nltk.download("punkt")
nltk.download("wordnet")

# Configurar FastAPI sin Swagger (/docs eliminado)
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
    docs_url=None
)

# Sirve los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura la carpeta de plantillas
templates = Jinja2Templates(directory="templates")

# Diccionario de sinónimos para mejorar la comprensión del chatbot
sinonimos_intenciones = {
    "consumo": ["consumo", "uso", "demanda", "gasto"],
    "generacion": ["generación", "producción", "creación", "suministro", "creacion", "produccion", "generacion"],
    "solar": ["solar", "fotovoltaica", "sol"],
    "undimotriz": ["undimotriz", "olas", "mareomotriz", "energía del mar"],
    "prediccion": ["predicción", "proyección", "futuro", "estimar"]
}

# Función para identificar la intención con sinónimos
def identificar_intencion(texto):
    palabras = word_tokenize(texto.lower())
    for clave, sinonimos in sinonimos_intenciones.items():
        if any(palabra in palabras for palabra in sinonimos):
            return clave
    return "desconocida"

# Suponiendo que esta función ya la tienes implementada
def obtener_pais(texto, df):
    for pais in df["country"].unique():
        if pais.lower() in texto.lower():
            return pais
    return None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat")
async def chat_api(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Llamar a la lógica completa del chatbot
    respuesta = await chatbot(query=user_message)
    return JSONResponse(content={"response": respuesta["respuesta"]})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/portal", response_class=HTMLResponse)
async def portal_page(request: Request):
    return templates.TemplateResponse("portal.html", {"request": request})


# ✅ Variables globales para los modelos
modelo_consumo = None
modelo_generacion = None

def entrenar_modelos():
    global modelos_prediccion
    try:
        print("🚀 Iniciando entrenamiento de modelos...")
        df = pd.read_csv("World Energy Consumption.csv").dropna(subset=['year'])

        # ✅ Filtrar solo el país de interés (ejemplo: Colombia) si es necesario
        # df = df[df['country'] == 'Colombia']  # Descomenta si quieres entrenar solo para Colombia

        # ✅ Rellenar valores nulos con la media
        df.fillna(df.mean(numeric_only=True), inplace=True)

        X = df[['year']]
        columnas_energia = {
            "consumo_total": "primary_energy_consumption",
            "generacion_total": "electricity_generation",
            "solar": "solar_electricity",
            "eolica": "wind_electricity",
            "hidroelectrica": "hydro_electricity",
            "carbon": "coal_electricity",
            "gas": "gas_electricity",
            "petroleo": "oil_electricity",
            "renovables": "renewables_electricity",
            "undimotriz": "wave_energy"
        }

        # ✅ Entrenar modelo para cada fuente de energía
        for nombre, columna in columnas_energia.items():
            if columna in df.columns:
                y = df[columna]
                if not y.isnull().all():
                    modelo = LinearRegression()
                    modelo.fit(X, y)
                    modelos_prediccion[nombre] = modelo
                    print(f"✅ Modelo entrenado para {nombre}.")
                else:
                    print(f"⚠️ Columna '{columna}' vacía, no se entrenó modelo.")
            else:
                print(f"⚠️ Columna '{columna}' no encontrada en el dataset.")

        if not modelos_prediccion:
            raise ValueError("❌ No se pudo entrenar ningún modelo.")

    except Exception as e:
        print(f"❌ Error al entrenar los modelos: {str(e)}")



@app.on_event("startup")
async def startup_event():
    entrenar_modelos()  # ✅ Entrenamiento automático al iniciar el servidor

# ✅ Detección de intenciones
def obtener_intencion(pregunta):
    palabras_clave = word_tokenize(pregunta.lower())
    intenciones = {
        "solar": ["solar"],
        "eolica": ["eólica", "viento"],
        "hidroelectrica": ["hidroeléctrica", "agua"],
        "carbon": ["carbón"],
        "gas": ["gas"],
        "petroleo": ["petróleo"],
        "undimotriz": ["undimotriz", "olas", "mar"],
        "consumo": ["consumo", "gasto", "uso"],
        "generacion": ["generación", "producir", "producción"],
        "renovable": ["renovable", "renovables"],
        "prediccion": ["predicción", "futuro", "proyección"]
    }
    for intencion, claves in intenciones.items():
        if any(p in palabras_clave for p in claves):
            return intencion
    return "desconocida"

# ✅ Declarar variables globales para todos los modelos
modelos_prediccion = {}

# ✅ Lista de columnas a modelar
columnas_energia = {
    "consumo_total": "primary_energy_consumption",
    "generacion_total": "electricity_generation",
    "solar": "solar_electricity",
    "eolica": "wind_electricity",
    "hidroelectrica": "hydro_electricity",
    "carbon": "coal_electricity",
    "gas": "gas_electricity",
    "petroleo": "oil_electricity",
    "renovables": "renewables_electricity",
    "undimotriz": "wave_energy"
}


# ✅ Filtrar país mencionado
def obtener_pais(pregunta, df):
    paises = df['country'].unique()
    for pais in paises:
        if pais.lower() in pregunta.lower():
            return pais
    return "World"


def extraer_anios(pregunta):
    
    # ✅ Detecta un rango de años (ejemplo: 2025 a 2027)
    rango = re.findall(r"(\d{4})\s*(?:a|-|hasta|y)\s*(\d{4})", pregunta)
    if rango:
        inicio, fin = map(int, rango[0])
        return list(range(inicio, fin + 1))  # ✅ Incluye ambos extremos del rango

    # ✅ Detecta años individuales
    anios = list(map(int, re.findall(r"\b\d{4}\b", pregunta)))
    return sorted(list(set(anios))) if anios else [2022]


@app.get("/chat/endpoint")
async def chatbot(query: str):
    try:
        df = pd.read_csv("World Energy Consumption.csv")
        if df.empty:
            return {"respuesta": "❌ No se encontraron datos en el dataset."}

        pais = obtener_pais(query, df) or "World"
        anios_mencionados = sorted(extraer_anios(query))  # ✅ Aseguramos el orden ascendente
        ultimo_anio_dataset = df["year"].max()
        primer_anio_dataset = df["year"].min()

        # ✅ Incrementos históricos para consumo y generación
        consumo_2000 = df[(df["year"] == 2000) & (df["country"] == pais)]["primary_energy_consumption"].values[0]
        consumo_2022 = df[(df["year"] == 2022) & (df["country"] == pais)]["primary_energy_consumption"].values[0]
        generacion_2000 = df[(df["year"] == 2000) & (df["country"] == pais)]["electricity_generation"].values[0]
        generacion_2022 = df[(df["year"] == 2022) & (df["country"] == pais)]["electricity_generation"].values[0]

        incremento_consumo_anual = ((consumo_2022 / consumo_2000) ** (1 / 22)) - 1
        incremento_generacion_anual = ((generacion_2022 / generacion_2000) ** (1 / 22)) - 1

        # ✅ Tipos de energía con columnas correspondientes
        tipos_energia = {
            "Solar": "solar_electricity",
            "Eólica": "wind_electricity",
            "Hidroeléctrica": "hydro_electricity",
            "Carbón": "coal_electricity",
            "Gas": "gas_electricity",
            "Petróleo": "oil_electricity",
            "Renovables": "renewables_electricity",
            "Undimotriz": "wave_energy"
        }

        # ✅ Emojis para cada tipo de energía
        emojis_energia = {
            "Solar": "🌞",
            "Eólica": "💨",
            "Hidroeléctrica": "💧",
            "Undimotriz": "🌊",
            "Renovables": "🌿",
            "Carbón": "🪨",
            "Gas": "🔥",
            "Petróleo": "🛢️"
        }

        # ✅ Orden de presentación
        orden_energia = ["Solar", "Eólica", "Hidroeléctrica", "Undimotriz", "Renovables", "Carbón", "Gas", "Petróleo"]

        # ✅ Cálculo de incrementos por tipo de energía
        incrementos_energia = {}
        for nombre, columna in tipos_energia.items():
            try:
                energia_2000 = df[(df["year"] == 2000) & (df["country"] == pais)][columna].values[0]
                energia_2022 = df[(df["year"] == 2022) & (df["country"] == pais)][columna].values[0]
                incremento_anual = ((energia_2022 / energia_2000) ** (1 / 22)) - 1 if energia_2000 > 0 else 0
                incrementos_energia[nombre] = (energia_2022, incremento_anual)
            except:
                incrementos_energia[nombre] = (0, 0)

        # ✅ Generación de la respuesta
        respuesta = ""
        for anio in anios_mencionados:
            if anio <= ultimo_anio_dataset:
                # 📊 Datos históricos
                df_anio = df[(df['year'] == anio) & (df['country'] == pais)]
                if not df_anio.empty:
                    respuesta += (
                        f"📊 **Datos históricos para {pais} en {anio}:**\n\n"
                        f"🔋 **Consumo total:** {df_anio['primary_energy_consumption'].values[0]:.2f} TWh\n"
                        f"⚡ **Generación total:** {df_anio['electricity_generation'].values[0]:.2f} TWh\n\n"
                        f"🌱 **Detalle por tipo de energía:**\n"
                    )
                    for nombre in orden_energia:
                        columna = tipos_energia.get(nombre)
                        if columna and columna in df_anio.columns:
                            valor = df_anio[columna].values[0]
                            respuesta += f"{emojis_energia.get(nombre, '🔋')} {nombre}: {valor:.2f} TWh\n"
                    respuesta += "\n"

                else:
                    respuesta += f"⚠️ No se encontraron datos para {anio}.\n\n"

            else:
                # 🔮 Predicción futura basada en incrementos históricos
                anios_futuros = anio - 2022
                consumo_predicho = consumo_2022 * ((1 + incremento_consumo_anual) ** anios_futuros)
                generacion_predicha = generacion_2022 * ((1 + incremento_generacion_anual) ** anios_futuros)

                respuesta += (
                    f"🔮 **Predicciones para {pais} en {anio}:**\n\n"
                    f"⚡ **Generación total estimada:** {generacion_predicha:.2f} TWh\n"
                    f"🔋 **Consumo total estimado:** {consumo_predicho:.2f} TWh\n\n"
                    f"🌱 **Detalle por tipo de energía:**\n"
                )

                # ✅ Desglose ordenado y con emojis, con saltos de línea claros
                for nombre in orden_energia:
                    valor_base, incremento_anual = incrementos_energia.get(nombre, (0, 0))
                    valor_predicho = valor_base * ((1 + incremento_anual) ** anios_futuros) if valor_base > 0 else 0
                    respuesta += f"{emojis_energia.get(nombre, '🔋')} {nombre}: {valor_predicho:.2f} TWh\n"

                respuesta += "\n"  # 🔄 Salto de línea al final de cada año

        if not respuesta.strip():
            respuesta = "🤖 Lo siento, aún estoy aprendiendo. Intenta preguntarme sobre años con datos o predicciones futuras."

        return {"respuesta": respuesta}

    except Exception as e:
        return {"respuesta": f"⚠️ Error al procesar la solicitud: {str(e)}"}