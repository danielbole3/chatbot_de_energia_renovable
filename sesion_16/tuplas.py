#--------------------------------------pagina 7-------------------------------------
# tuplas
#las tuplas son inmutables, lo que significa que no puedes modificar sus elementos una vez creadas
# puedes generar una tupla con la función tuple() o tupla()

herramientas_de_goku = ("baculo sagrado", "nube voladora", "semillas del ermitaño")

# indices y acceso a elementos
# los elementos de la tupla tambien se enumeran de 0 en adelante
# puedes acceder a los elementos de la tupla utilizando los índices

herramienta_1_de_goku = herramientas_de_goku[0]
print(herramienta_1_de_goku)
herramienta_2_de_goku = herramientas_de_goku[1]
print(herramienta_2_de_goku)

#----------------------------------------pagina 8-----------------------------------------

# longitud de una tupla: puedes obtener la longitud de una tupla utilizando la función len()
#la longitud es el numero de elementos en la tupla

longitud = len(herramientas_de_goku)
print(longitud)

# inmutabilidad
# las tuplas son inmutables lo que significa que no puedes cambiar sus elementos

#print(herramientas_de_goku)
#herramientas_de_goku[0] = "radar del dragon"
#print(herramientas_de_goku)

# empaquetado y desempaquetado
# podemos empaquetar varios valores en una tupla y luego desempaquetar esos valores en 
# variables individuales

print(herramientas_de_goku)
#asignamos cada herramienta a una variable individual
herramienta_1_de_goku, herramienta_2_de_goku, herramienta_3_de_goku = herramientas_de_goku  
print(herramienta_1_de_goku)
print(herramienta_2_de_goku)
print(herramienta_3_de_goku)

# nota importante el numero de valiables debe ser igual al numero de elementos en la tupla
# si la tupla tiene 3 elementos y queremos asignar 4 variables, se producira un error

# solucion con "*": si no sabes cuantos elementos tienes en la tupla, puedes usar "*"

herramientas_1_de_goku, *resto_de_herramientas = herramientas_de_goku
print(herramienta_1_de_goku)
print(resto_de_herramientas)

# ------------------------------Página 9-----------------------------
# Uso de Iteraciones: Las tuplas se utilizan comunmente en situaciones donde se necesita una
# estructura de datos inmutables, como claves de un diccionario o elementos de un conjunto.

# Tuplas anidadas: Puedes tener tuplas dentro de tuplas, creando así estructuras de datos 
# más complejas.

# Vamos a crear una tupla anidada que contenga sub-tuplas con información básica de las herramientas de Goku.

tupla_anidada = (("Báculo sagrado", "Nube voladora", "semillas del Ermitaño"), ("radar del dragón", "esfera de cuatro estrellas", "colita de mono"))

print(tupla_anidada)

# Las tuplas son útiles cuando necesitas asegurarte de que los datos no cambien durante la 
# ejecución del programa y se utilizan comúnmente donde la inmutabilidad es importante.


