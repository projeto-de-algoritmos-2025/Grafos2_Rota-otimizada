import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import heapq
import pprint
from heapdict import heapdict

def salvar_grafo_txt(graph, filename="./logs/graph_object.txt"):
    """
    To usando pra salvar a estrutura interna do grafo e entender a estrutura dos dados.
    """
    pp = pprint.PrettyPrinter(indent=2, width=120, compact=False)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== graph._node ===\n")
        f.write(pp.pformat(graph._node))
        f.write("\n\n=== graph._adj ===\n")
        f.write(pp.pformat(graph._adj))
        f.write("\n\n=== graph._edge ===\n")
        f.write(pp.pformat(graph.edges))

def main():
    # nome do lugar para baixar o mapa
    place_name = "Tamandaré, Pernambuco, Brazil"

    print(f"Baixando mapa de: {place_name}")
    # O network_type pode ser 'drive', 'walk', 'bike', 'all', etc. Define o tipo de rotas a incluir. drive = estradas para carros
    graph = ox.graph_from_place(place_name, network_type="drive")
    print("Mapa baixado com sucesso!")

    print("Plotando o grafo do mapa...")
    fig, ax = ox.plot_graph(graph, node_size=0, edge_color="gray", edge_linewidth=0.5)
    plt.show()
    print("Grafo plotado com sucesso!")

if __name__ == "__main__":
    main()