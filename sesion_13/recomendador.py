# importar la libreria csv para trabajar con archivos csv
import csv

#leer los datos del archivo csv
with open ('videos.csv', 'r') as file:
    reader = csv.DictReader(file)
    videos = list(reader)
# encontrar el video con la mayor calificación
mejor_video = max(videos, key=lambda x:float(x['Calificacion']))    
# imprimir el video con la calificación mayor
print("🎥 Video Recomendado:")
print(f"Nombre: {mejor_video['Video']}")
print(f"Calificación: {mejor_video['Calificacion']}")