#--------------------------pagina 3------------------------------#
# contenedores
# listas
# las listas van en corchetes [] 

tripulantes_de_los_mugiwara = ["zoro", "sanji", "nami", "robin", "luffy",]

print(tripulantes_de_los_mugiwara)
print(tripulantes_de_los_mugiwara[0])

# indice y acceso a elementos: los elementos de una lista se enumeran del 0 en adelante
primer_tripulante_de_los_mugiwara = tripulantes_de_los_mugiwara[0]
print(primer_tripulante_de_los_mugiwara)

# crea una variable llamada segundo_tripulante_de_los_mugiwara y muestralo en la pantalla 
segundo_tripulante_de_los_mugiwara = tripulantes_de_los_mugiwara[1]
print(segundo_tripulante_de_los_mugiwara)

#--------------------------pagina 4------------------------------#
# longitud de una lista: puedes obtener la longitud de una lista con la funcion len()
# la longitud es el numero de elementos en la lista
longitud = len(tripulantes_de_los_mugiwara)
print(longitud)
print(tripulantes_de_los_mugiwara)
tripulantes_de_los_mugiwara[3] = "robin"
print(tripulantes_de_los_mugiwara)


#--------------------------pagina 5------------------------------#

# operaciones comunes
# puedes realizar diversas operaciones con listas como agregar elementos, eliminar elementos, extender listas, etc.
#agregar elementos al final de una lista con la funcion append()
print(tripulantes_de_los_mugiwara)
tripulantes_de_los_mugiwara.append("chopper")
print(tripulantes_de_los_mugiwara)
# tambien podrias eliminar elementos por valor
print(tripulantes_de_los_mugiwara)
tripulantes_de_los_mugiwara.remove("chopper")
# puedes extender una lista con otra con la funcion extend()
cuatro_younkos_del_mar = ["shanks", "barba blanca", "big mom", "shiroigue", 4]
print(cuatro_younkos_del_mar)
tripulantes_de_los_mugiwara.extend(cuatro_younkos_del_mar)
print(tripulantes_de_los_mugiwara)

# agregar los almirantes_de_la_marina a la lista tripulantes_de_los_mugiwara
# usa la funcion extend() con la lista almirantes_de_la_marina
# fuyitora kizaru ruokugyo

almirantes_de_la_marina = ["fuyitora", "kizaru", "ruokugyo"]
tripulantes_de_los_mugiwara.extend(almirantes_de_la_marina)
print(tripulantes_de_los_mugiwara)

#--------------------------pagina 6------------------------------#
#puedes optener una porcion de una lista con la funcion slice()

longitud = len(tripulantes_de_los_mugiwara)
print(longitud)
cantidad_de_younkos = tripulantes_de_los_mugiwara[0:6]
print(cantidad_de_younkos)

#las listas son herramientas fundamentales en python y se utilizan 
#para almacenar y manipular datos de manera eficiente
