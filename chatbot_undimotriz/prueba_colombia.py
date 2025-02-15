import pandas as pd

# Cargar el dataset
df = pd.read_csv("World Energy Consumption.csv")

# Filtrar por el país y año que agregaste en Swagger
country = "Colombia"  # Cambia esto al país que ingresaste
year = 2024  # Cambia esto al año que ingresaste

df_filtrado = df[(df["country"] == country) & (df["year"] == year)]

if df_filtrado.empty:
    print("❌ El dato NO se guardó correctamente.")
else:
    print("✅ El dato SE guardó correctamente:")
    print(df_filtrado)