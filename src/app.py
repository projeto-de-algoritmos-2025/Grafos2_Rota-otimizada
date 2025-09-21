import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import heapq
import pprint
from heapdict import heapdict
import folium

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
    # TODO: implementar o weight_type='speed' aqui ou em outra função? (lembrando que o peso para as velocidades deve ser negativo para pegar sempre a maior velocidade - "ah mas Dijkstra não funciona com pesos negativos" - sei disso, mas nenhuma velocidade será positiva, o menor peso (mais negativo) sempre será a maior velocidade)
    # TODO: tratar o caso de não existir caminho entre os nós
    # TODO: tratar o caso de o start_node ou end_node não existirem no grafo
    # TODO: tratar o caso de o start_node ser igual ao end_node
    # TODO: tratar o caso de o weight_type ser inválido
    # TODO: comparar o tempo de execução usando heapq vs heapdict

    # para simularmos a heap do jeito que aprendemos, precisamos usar 2 estruturas de dados, uma para o atual custo e outra para saber a ordem minHeap
    cheapest_path = {node: float('inf') for node in graph.nodes}
    cheapest_path[start_node] = 0

    # A gnt pode tentar usar heapdict para a estrutura da minHeap (com a heapq não é possivel apenas atualizar o custo de um nó já existente, ai inserimos o mesmo nó várias vezes com custos diferentes, mas eles são descartados logo quando retirados da heap, então não sei o quanto isso impacta na complexidade)
    #minHeap = heapdict()
    minHeap = [(0, start_node)]
    #minHeap[start_node] = 0
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
                #minHeap[neighbour] = new_cost
                heapq.heappush(minHeap, (new_cost, neighbour))


    # "Backtracking" do caminho mais curto
    path = []
    node = end_node
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()

    return path, cheapest_path[end_node]

def set_edge_speed(graph):
    """
    Em construção :) 
    Adiciona um atributo 'speed' às arestas do grafo com base no tipo de via e atribui valores de velocidade.
    """
    # OBS: esses TODOs não são necessariamente nessa função
    # TODO: Iterar sobre o grafo e definir a velocidade com base no tipo de via
    # TODO: descobrir todos os tipos de vias presentes no grafo (usar o check_highways.py)
    # TODO: temos a velocidade, mas vamos precisar do tempo tmb, que vai ser length/Media(speed), então quando o wight_type do dijkstra for speed, vamos usar tanto length quanto speed
    # TODO: Não sei se a gnt adiciona é no graph._edge ou graph._adj
    # inicializa todas as velocidades como 0
    nx.set_edge_attributes(graph, float(0), name="speed")

    highway_speeds = {
        'secondary_link': 50,
        'primary_link': 60,
        'path': 5,
        'pedestrian': 5,
        'tertiary': 40,
        'unclassified': 30,
        'service': 15,
        'primary': 60,
        'secondary': 50,
        'living_street': 10,
        'residential': 20,
        'footway': 5,
        'construction': 5,
        'track': 15,
    }

def plot_city_graph(graph, route):
    """
    Plota o grafo com a rota destacada.
    """
    print("Plotando o grafo do mapa...")
    fig, ax = ox.plot_graph(graph, node_size=0, edge_color="gray", edge_linewidth=0.5)
    plt.show()
    print("Grafo plotado com sucesso!")

def plot_route_on_map(graph, shortest_path, fastest_path):
    print("Gerando mapa interativo...")

    # Pegando as coordenadas do ponto de partida para centralizar o mapa
    start_node = shortest_path[0]
    start_location = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])

    # Cria um mapa Folium manualmente, centrado no ponto de partida
    m = folium.Map(location=start_location, zoom_start=16)

    # Criam uma lista de tuplas (latitude, longitude) para cada nó do caminho
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]

    # Usando a PolyLine pra desenhar uma linha conectando as coordenadas
    folium.PolyLine(locations=route_coords, color='blue', weight=5).add_to(m)

    # Adiciona marcadores de início e fim 
    end_node = shortest_path[-1]
    end_location = (graph.nodes[end_node]['y'], graph.nodes[end_node]['x'])
    folium.Marker(location=start_location, popup='Início', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end_location, popup='Fim', icon=folium.Icon(color='red')).add_to(m)

    # Ajusta o zoom para que toda a rota apareça na tela
    m.fit_bounds(folium.PolyLine(locations=route_coords).get_bounds())

    # 7. Salve o mapa final (note que salvamos 'm', o mapa original)
    m.save('rota_curta.html')
    print("Mapa salvo como 'rota_curta.html'. Abra este arquivo no seu navegador.")

def main():
    # nome do lugar para baixar o mapa
    place_name = "Tamandaré, Pernambuco, Brazil"

    print(f"Baixando mapa de: {place_name}")
    # O network_type pode ser 'drive', 'walk', 'bike', 'all', etc. Define o tipo de rotas a incluir. drive = estradas para carros
    graph = ox.graph_from_place(place_name, network_type="drive")
    print("Mapa baixado com sucesso!")

    nodes_list = list(graph.nodes)
    start_node = nodes_list[0]  # Pega o primeiro nó da lista
    end_node = nodes_list[-1]   # Pega o último nó da lista
    print(f"Nós de início e fim: {start_node}, {end_node}")
    print(f"\nCalculando a rota mais CURTA de {start_node} para {end_node}...")

    shortest_path, path_cost = dijkstra(graph, start_node, end_node, weight_type='length')
    
    if shortest_path and path_cost < float('inf'):
        print(f"Rota mais CURTA encontrada com {len(shortest_path)} nós.")
        print("Caminho:", shortest_path)
        print(f"Custo total (distância): {path_cost:.2f} metros")
        plot_route_on_map(graph, shortest_path, shortest_path)
    else:
        print("Nenhum caminho encontrado entre os nós especificados.")

if __name__ == "__main__":
    main()