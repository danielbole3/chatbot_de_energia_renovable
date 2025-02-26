import pandas as pd

# Cargar CSV
df = pd.read_csv("World Energy Consumption.csv")

# 🏷️ Mostrar tipos de datos de las columnas clave
print("🔍 Tipos de datos:")
print(df[['primary_energy_consumption', 'electricity_generation']].dtypes)

# 📊 Resumen estadístico para detectar valores extraños
print("\n📈 Resumen estadístico:")
print(df[['primary_energy_consumption', 'electricity_generation']].describe())

# 🔍 Ver cuántos valores nulos hay
print("\n⚠️ Valores nulos en las columnas clave:")
print(df[['primary_energy_consumption', 'electricity_generation']].isna().sum())

# 🧪 Mostrar las primeras 10 filas para revisión manual
print("\n📄 Primeras 10 filas de las columnas clave:")
print(df[['primary_energy_consumption', 'electricity_generation']].head(10))

# 🕵️ Mostrar filas con valores faltantes si existen
print("\n⚡ Filas con datos faltantes:")
print(df[df[['primary_energy_consumption', 'electricity_generation']].isna().any(axis=1)])
