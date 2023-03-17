
from node_data.neo4j_data.load_nodes import load_city_nodes, update_city_nodes, link_nodes
import concurrent.futures
from utils import *
# ciudades = ["Madrid", "París", "Berlín", "Londres", "Amsterdam", "Roma"]
# ciudades = ["Valladolid", "Burgos", "Ávila", "Salamanca", "Segovia", "Soria", "Palencia", "León", "Zamora"]
ciudades = ["Sevilla", "Zaragoza", "Valencia"]


def cargar_nodos():
    for ciudad in ciudades:
        load_city_nodes(ciudad)
        city_amenity_histogram(ciudad)


def crear_histograma(ciudad: str, limsup: int = None):
    if limsup is None:
        city_amenity_histogram(ciudad)
    else:
        city_amenity_histogram(ciudad, lim_sup=limsup)


# print("1. Cargar Nodos y Guardar Histograma \n2. Crear Histograma")
# opcion = input("> Opción: ")
# while opcion not in ("2", "1"):
#     opcion = input("> Opción: ")

# if opcion == "1":
#     cargar_nodos()
# else:
#     for c in ciudades:
#         print(f">>>Ciudad: {c}")
#         limites = ""
#         while limites not in ("s", "n"):
#             limites = input("Quieres limites en las gráficas?(s/n):")
#         if limites == "n":
#             crear_histograma(c)
#         else:
#             limsup = int(input("Cuantas amenities mostrar?: "))
#             crear_histograma(c, limsup=limsup)
# amenity_similarity(r"../data/csv/amenity_similarity.csv")

if __name__ == "__main__":
    cargar_nodos()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(link_nodes, city, 100) for city in ciudades]
        concurrent.futures.wait(futures)
