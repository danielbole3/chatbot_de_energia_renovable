from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("es_core_news_sm")


# Crear la aplicación FastAPI
app = FastAPI()

# Montar la carpeta 'static' para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Diccionario para almacenar el nombre del usuario
user_data = {"name": None}


@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())

@app.get("/chat", response_class=HTMLResponse)
async def get_chat():
    with open("chat.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())
    
@app.get("/portal", response_class=HTMLResponse)
async def get_portal():
    with open("portal.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())

# Datos de preguntas y respuestas 
data = [
    {"category": "Viabilidad por región", "phrase": "¿Qué zonas del país son más efectivas para instalar paneles solares?"},
    {"category": "Época de productividad", "phrase": "¿Cuándo son más productivos los paneles solares?"},
    {"category": "Incentivos", "phrase": "¿Qué incentivos hay para paneles solares?"},
    {"category": "Sector agrícola", "phrase": "¿Es útil la energía solar para una finca hotel?"},
    {"category": "Sector agrícola", "phrase": "¿Cómo puede ayudar la energía solar en galpones?"},
    {"category": "Sector agrícola", "phrase": "¿Es rentable usar paneles solares en fincas lecheras?"},
    {"category": "Impacto ambiental", "phrase": "¿Qué beneficios ambientales ofrecen los paneles solares?"},
    {"category": "Vida útil", "phrase": "¿Cuánto tiempo duran los paneles solares?"},
    {"category": "Mantenimiento", "phrase": "¿Qué tipo de mantenimiento requieren los paneles solares?"},
    {"category": "Autonomía energética", "phrase": "¿Es posible ser completamente independiente con energía solar?"},
    {"category": "Energías renovables", "phrase": "¿Qué otras energías renovables existen además de la solar?"},
    {"category": "Almacenamiento", "phrase": "¿Qué tipo de baterías se usan para almacenar energía solar?"},
    {"category": "Rentabilidad", "phrase": "¿En cuánto tiempo se recupera la inversión en paneles solares?"},
    {"category": "Instalación", "phrase": "¿Es complicada la instalación de paneles solares?"},
    {"category": "Normatividad", "phrase": "¿Qué normativas existen en Colombia sobre energía solar?"},
    {"category": "Costo inicial", "phrase": "¿Cuál es el costo inicial promedio de un sistema de paneles solares?"},
    {"category": "Potencia requerida", "phrase": "¿Cómo se calcula la potencia necesaria para un hogar?"},
    {"category": "Clima y producción", "phrase": "¿Cómo afecta el clima la producción de energía solar?"},
    {"category": "Futuro", "phrase": "¿Cuál es el futuro de la energía solar en Colombia?"},
    {"category": "Empresas", "phrase": "¿Cómo pueden las empresas beneficiarse de la energía solar?"},
    {"category": "Ahorro", "phrase": "¿Cuánto se puede ahorrar al instalar paneles solares?"},
    {"category": "Innovación", "phrase": "¿Qué innovaciones existen actualmente en energía solar?"},
    {"category": "Desventajas", "phrase": "¿Cuáles son las desventajas de la energía solar?"},
    {"category": "Educación", "phrase": "¿Qué programas educativos promueven la energía solar?"},
    {"category": "Impacto en la factura", "phrase": "¿Cómo afecta la energía solar la factura eléctrica?"},
    {"category": "Residuos", "phrase": "¿Qué se hace con los paneles solares al final de su vida útil?"},
    {"category": "Zonas rurales", "phrase": "¿Cómo puede la energía solar beneficiar a zonas rurales?"},
    {"category": "Energía híbrida", "phrase": "¿Qué es un sistema híbrido de energía solar?"},
    {"category": "Durabilidad", "phrase": "¿Cómo se asegura la durabilidad de los paneles solares?"},
    {"category": "Microinversores", "phrase": "¿Qué son los microinversores en un sistema solar?"},
    {"category": "Tipos de paneles solares", "phrase": "¿Cuáles son los diferentes tipos de paneles solares?"},
    {"category": "Calidad de paneles solares", "phrase": "¿Cómo saber si un panel solar es de buena calidad?"},
    {"category": "Costo por watt", "phrase": "¿Cuál es el costo promedio por watt de un panel solar?"},
    {"category": "Inversores", "phrase": "¿Qué función cumplen los inversores en un sistema solar?"},
    {"category": "Vida útil de paneles solares", "phrase": "¿Cuál es la vida útil promedio de los paneles solares en Colombia?"},
    {"category": "Garantías", "phrase": "¿Qué garantías ofrecen los fabricantes de paneles solares?"},
    {"category": "Instalación en viviendas", "phrase": "¿Qué se necesita para instalar paneles solares en una vivienda?"},
    {"category": "Energía solar en la industria", "phrase": "¿Cómo se utiliza la energía solar en la industria colombiana?"},
    {"category": "Normas técnicas", "phrase": "¿Qué normas técnicas deben cumplir los paneles solares en Colombia?"},
    {"category": "Financiación", "phrase": "¿Existen planes de financiación para paneles solares en Colombia?"},
    {"category": "Mantenimiento avanzado", "phrase": "¿Qué implica un mantenimiento avanzado de los paneles solares?"},
    {"category": "Paneles solares bifaciales", "phrase": "¿Qué son los paneles solares bifaciales y cómo funcionan?"},
    {"category": "Instalaciones en zonas rurales", "phrase": "¿Cómo se adaptan los paneles solares para zonas rurales en Colombia?"},
    {"category": "Producción local", "phrase": "¿Se fabrican paneles solares en Colombia?"},
    {"category": "Impacto ambiental en la producción", "phrase": "¿Qué impacto ambiental tiene la producción de paneles solares?"},
    {"category": "Desempeño en climas fríos", "phrase": "¿Cómo afectan los climas fríos al desempeño de los paneles solares?"},
    {"category": "Programas gubernamentales", "phrase": "¿Qué programas gubernamentales promueven el uso de energía solar en Colombia?"},
    {"category": "Baterías de respaldo", "phrase": "¿Qué tipos de baterías se recomiendan como respaldo para sistemas solares?"},
    {"category": "Desventajas de los sistemas solares", "phrase": "¿Cuáles son las principales desventajas de los sistemas solares?"},
    {"category": "Sistemas solares híbridos", "phrase": "¿Qué son los sistemas solares híbridos y cuáles son sus ventajas?"},
]


responses = {
    "Viabilidad por región": "Las zonas con mayor irradiación solar, como La Guajira, son ideales para paneles solares.",
    "Época de productividad": "Los meses con menos lluvias y más sol son los más productivos para los paneles solares.",
    "Incentivos": "Existen incentivos fiscales en Colombia para fomentar la instalación de paneles solares.",
    "Sector agrícola": "La energía solar es altamente útil en el sector agrícola para riego, iluminación y otros usos.",
    "Impacto ambiental": "Los paneles solares reducen la dependencia de combustibles fósiles, disminuyendo las emisiones de CO2.",
    "Vida útil": "La vida útil promedio de un panel solar es de 25 a 30 años.",
    "Mantenimiento": "El mantenimiento consiste principalmente en limpieza y revisiones anuales.",
    "Autonomía energética": "Es posible alcanzar la independencia energética combinando paneles solares y baterías.",
    "Energías renovables": "Además de la solar, existen energías eólica, geotérmica, hidráulica y biomasa.",
    "Almacenamiento": "Las baterías de litio son las más utilizadas por su eficiencia y durabilidad.",
    "Rentabilidad": "La inversión se recupera en promedio en 5 a 10 años dependiendo del consumo.",
    "Instalación": "La instalación requiere de profesionales certificados para garantizar un sistema seguro.",
    "Normatividad": "En Colombia, la Ley 1715 de 2014 regula el uso de energías renovables.",
    "Costo inicial": "El costo inicial varía según el tamaño del sistema, desde COP 10 millones en adelante.",
    "Potencia requerida": "Se calcula según el consumo energético promedio del hogar en kWh.",
    "Clima y producción": "Los días nublados reducen la producción, pero los sistemas siguen generando energía.",
    "Futuro": "La energía solar está en constante crecimiento gracias a los avances tecnológicos y mayor accesibilidad.",
    "Empresas": "Las empresas pueden reducir costos operativos y mejorar su imagen ambiental usando energía solar.",
    "Ahorro": "El ahorro depende del consumo y el costo de la energía, pero puede llegar al 50% o más.",
    "Innovación": "Los paneles solares bifaciales y los sistemas flotantes son algunas innovaciones recientes.",
    "Desventajas": "Las principales desventajas son el costo inicial alto y la dependencia de la luz solar.",
    "Educación": "Programas como el SENA promueven el aprendizaje en energías renovables.",
    "Impacto en la factura": "La energía solar puede reducir la factura eléctrica a cero en algunos casos.",
    "Residuos": "Los paneles solares son reciclables en un 80%, reduciendo el impacto ambiental.",
    "Zonas rurales": "En zonas rurales, los paneles solares pueden proveer energía en áreas sin conexión a la red.",
    "Energía híbrida": "Un sistema híbrido combina energía solar con otras fuentes, como la red eléctrica.",
    "Durabilidad": "La calidad de los materiales y el mantenimiento adecuado aseguran la durabilidad.",
    "Microinversores": "Los microinversores convierten la energía directamente en cada panel, aumentando la eficiencia.",
    "Tipos de paneles solares": "Existen principalmente tres tipos: monocristalinos, policristalinos y de película delgada. Los monocristalinos son los más eficientes.",
    "Calidad de paneles solares": "La calidad se evalúa por la eficiencia, la resistencia a condiciones climáticas extremas y las certificaciones internacionales como TUV y IEC.",
    "Costo por watt": "En Colombia, el costo promedio por watt instalado varía entre COP 3,500 y 5,000 dependiendo del tipo de sistema.",
    "Inversores": "Los inversores convierten la corriente directa generada por los paneles solares en corriente alterna, apta para el consumo doméstico o industrial.",
    "Vida útil de paneles solares": "La vida útil promedio es de 25 a 30 años, dependiendo del mantenimiento y la calidad del panel.",
    "Garantías": "Los fabricantes suelen ofrecer garantías de 10 a 25 años sobre la eficiencia y materiales del panel.",
    "Instalación en viviendas": "Se necesita una evaluación técnica, espacio adecuado en el techo, y permisos según las normativas locales.",
    "Energía solar en la industria": "En la industria, la energía solar se utiliza para reducir costos energéticos y para procesos como calentamiento de agua y generación eléctrica.",
    "Normas técnicas": "Los paneles solares deben cumplir con normas como la IEC 61215 para garantizar durabilidad y rendimiento.",
    "Financiación": "En Colombia, existen bancos y programas gubernamentales que ofrecen financiación a largo plazo con tasas preferenciales para proyectos solares.",
    "Mantenimiento avanzado": "Incluye la inspección de conexiones eléctricas, limpieza profunda y pruebas de eficiencia.",
    "Paneles solares bifaciales": "Capturan energía solar por ambas caras, aumentando la eficiencia en un 10-20%.",
    "Instalaciones en zonas rurales": "En estas zonas, se suelen usar sistemas solares autónomos con baterías debido a la falta de acceso a la red eléctrica.",
    "Producción local": "En Colombia, algunas empresas fabrican componentes de paneles solares, pero la mayoría son importados.",
    "Impacto ambiental en la producción": "Aunque requieren energía para su fabricación, los paneles solares tienen una huella de carbono significativamente menor que los combustibles fósiles.",
    "Desempeño en climas fríos": "Los paneles solares funcionan mejor en temperaturas bajas ya que el calor puede reducir su eficiencia.",
    "Programas gubernamentales": "El Gobierno Colombiano ofrece incentivos como exenciones tributarias para promover la instalación de sistemas solares.",
    "Baterías de respaldo": "Las baterías de litio son las más recomendadas debido a su durabilidad y eficiencia.",
    "Desventajas de los sistemas solares": "El costo inicial es elevado, y su rendimiento depende de la ubicación y la radiación solar disponible.",
    "Sistemas solares híbridos": "Combinan energía solar con otras fuentes, como generadores eléctricos, para mayor confiabilidad.",
}



# Modelo de entrada para preguntas y nombre
class UserQuery(BaseModel):
    question: str

class NameRequest(BaseModel):
    name: str

@app.post("/set_name")
async def set_name(request: NameRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="El nombre no puede estar vacío.")
    user_data["name"] = request.name.strip()
    return {"message": f"¡Hola, {user_data['name']}! Bienvenido al Chatbot de Energías Renovables. ¿En qué puedo ayudarte?"}

def find_best_match_with_spacy(input_text):
    user_doc = nlp(input_text.lower())
    user_keywords = [token.lemma_ for token in user_doc if not token.is_stop and not token.is_punct]

    best_match = None
    highest_similarity = 0

    for item in data:
        category_doc = nlp(item["phrase"].lower())
        category_keywords = [token.lemma_ for token in category_doc if not token.is_stop and not token.is_punct]

        common_keywords = set(user_keywords) & set(category_keywords)
        similarity_score = len(common_keywords) / len(set(category_keywords))

        if similarity_score > highest_similarity and similarity_score > 0.3:
            highest_similarity = similarity_score
            best_match = item["category"]

    return best_match


@app.post("/chat")
async def chat(request: UserQuery):
    if not user_data["name"]:
        return {"response": "Por favor, proporciona tu nombre primero."}
    category = find_best_match_with_spacy(request.question.lower())
    response = responses.get(category, "Lo siento, no entiendo la pregunta. ¿Puedes reformularla?")

    return {"response": response}

 
solar_production_by_department = {
    "amazonas": 160,
    "antioquia": 150,
    "arauca": 170,
    "atlantico": 200,
    "bolivar": 190,
    "boyaca": 140,
    "caldas": 130,
    "caqueta": 150,
    "casanare": 170,
    "cauca": 150,
    "cesar": 180,
    "choco": 120,
    "cordoba": 190,
    "cundinamarca": 140,
    "guainia": 160,
    "guaviare": 160,
    "huila": 160,
    "la guajira": 210,
    "magdalena": 200,
    "meta": 160,
    "nariño": 130,
    "norte de santander": 170,
    "putumayo": 140,
    "quindio": 130,
    "risaralda": 130,
    "san andres y providencia": 190,
    "santander": 160,
    "sucre": 190,
    "tolima": 150,
    "valle del cauca": 140,
    "vaupes": 160,
    "vichada": 170,
    "bogota": 130,
}
# Modelo de solicitud para calcular el ahorro
class SavingsRequest(BaseModel):
    department: str
    monthly_consumption_kwh: float
    price_per_kwh: float

# Modelo de solicitud para calcular el ahorro (sin cambios previos)

@app.post("/calculate_savings")
async def calculate_savings(request: SavingsRequest):
    normalized_department = request.department.lower()
    if normalized_department not in solar_production_by_department:
        raise HTTPException(
            status_code=400,
            detail=f"Departamento no reconocido. Los departamentos disponibles son: {', '.join(solar_production_by_department.keys())}."
        )

    monthly_solar_production = solar_production_by_department[normalized_department]
    savings_per_month = min(request.monthly_consumption_kwh, monthly_solar_production) * request.price_per_kwh
    annual_savings = savings_per_month * 12
    savings_3_years = annual_savings * 3
    savings_15_years = annual_savings * 15

    return {
        "message": (
            f"En {request.department}, con un consumo mensual de {request.monthly_consumption_kwh} kWh "
            f"y un precio de {request.price_per_kwh} COP por kWh, podrías ahorrar aproximadamente:\n"
            f"- {round(annual_savings, 2)} COP al año instalando paneles solares.\n"
            f"- {round(savings_3_years, 2)} COP en 3 años.\n"
            f"- {round(savings_15_years, 2)} COP en 15 años."
        ),
        "annual_savings": annual_savings,  # Incluimos el ahorro anual en la respuesta JSON
        "savings_3_years": savings_3_years,  # Incluimos el ahorro a 3 años
        "savings_15_years": savings_15_years  # Incluimos el ahorro a 15 años
    }
