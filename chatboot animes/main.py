# importa la clase FastAPI del framework FastAPI
from fastapi import FastAPI

app = FastAPI() # crea una instancia de la clase FastAPI
app.title = "mi aplicacion de anime"

@app.get('/', tags=["Home"]) # define una ruta para el método GET
def menssage(): # definimos una funcion de la ruta 
    return "bienvenido al chatboot de animes del bootcam_ia"