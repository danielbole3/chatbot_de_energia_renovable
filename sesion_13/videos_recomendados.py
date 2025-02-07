import csv

#leer los datos del archivo csv
with open('videos.csv', 'r') as file:  
    reader = csv.DictReader(file)   
    file = list(reader)

#Encontrar el video con más likes

mejor_video = max(file, key=lambda x:float(x['Calificación']))

# Mostrar el video recomendado
print("🎥 Video Recomendado:")
print(f"Nombre: {mejor_video['Video']}")
print(f"Calificación: {mejor_video['Calificación']}")