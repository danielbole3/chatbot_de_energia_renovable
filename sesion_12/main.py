# importaremos la libreria pandas
# que es fundamental para la manipulacion de datos

import pandas as pd 

# definiremos la ruta del archivo
path = "Online_Retail.csv"

#lee el archivo
retail_data = pd.read_csv(path, encoding='latin-1')

#imprime el tipo de dato
print(type(retail_data))

#imprime el contenido
print(retail_data)