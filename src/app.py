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

def dijkstra(graph, start_node, end_node, weight_type):
    """
    weight_type='length'
        Calcula a rota mais curta entre dois nós usando o algoritmo de Dijkstra.
        O peso da aresta é a distância ('length').
    weight_type='speed'
        Calcula a rota mais rápida entre dois nós usando o algoritmo de Dijkstra.
        O peso da aresta é a velocidade média da via ('speed').
    """
    
    # para simularmos a heap do jeito que aprendemos, precisamos usar 2 estruturas de dados, uma para o atual custo e outra para saber a ordem de visita
    cheapest_path = {node: float('inf') for node in graph.nodes}
    cheapest_path[start_node] = 0

    # vamos utilizar a heapdict para a estrutura da minHeap, pois com a heapq não seria possivel apenas atualizar o custo de um nó já existente, teriamos que inserir o mesmo nó várias vezes com custos diferentes e eles seriam descartados quando retirados da heap
    minHeap = [(0, start_node)]
    heapq.heapify(minHeap)

    predecessors = {node : None for node in graph.nodes}

    while minHeap:
        #current_cost, node = minHeap.popitem()
        current_cost, node = heapq.heappop(minHeap)

        # se chegamos no nó final (ou o nó de destino foi removido), podemos parar
        if node == end_node:
            break

        # se o custo atual é maior que o custo mais barato conhecido, pulamos para a próxima iteração do while
        if current_cost > cheapest_path[node]:
            continue

        # iteramos sobre os vizinhos do nó atual
        for _, neighbour, k, data in graph.edges(node, keys=True, data=True):
            weight = data.get(weight_type, 1)
            new_cost = cheapest_path[node] + weight

            if new_cost < cheapest_path[neighbour]:
                cheapest_path[neighbour] = new_cost
                predecessors[neighbour] = node
                # atualiza o custo na heap e dale siftup
                heapq.heappush(minHeap, (new_cost, neighbour))


    # "Backtracking" do caminho mais curto
    path = []
    node = end_node
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()

    return path, cheapest_path[end_node]

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