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
    # TODO: implementar o weight_type='speed' aqui ou em outra função? (lembrando que o peso para as velocidades deve ser negativo para pegar sempre a maior velocidade - "ah mas Dijkstra não funciona com pesos negativos" - sei disso, mas nenhuma velocidade será positiva, o menor peso (mais negativo) sempre será a maior velocidade) ---- acho que é melhor implementar aqui mesmo para não ter que duplicar o código
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
            if weight_type == 'length':
                weight = data.get('length', 1)
            elif weight_type == 'speed':
                # Calcula o tempo de viagem como distância/velocidade
                length = data.get('length', 1)  # distância em metros
                speed = data.get('speed', 30)   # velocidade em km/h
                # Converte velocidade de km/h para m/s: speed_ms = speed * 1000 / 3600
                speed_ms = speed * (1000 / 3600)
                weight = length / speed_ms  # tempo em segundos
            else:
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
    Adiciona um atributo 'speed' às arestas do grafo com base no tipo de via e atribui valores de velocidade.
    """

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

    # inicializa todas as velocidades como 30 km/h (padrão)
    nx.set_edge_attributes(graph, 30, name="speed")

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
    
    # Itera sobre todas as arestas e define a velocidade baseada no tipo de via
    for u, v, k, data in graph.edges(keys=True, data=True):
        highway_type = data.get('highway', 'unclassified')
        if isinstance(highway_type, list):
            # Se highway for uma lista, pega o primeiro elemento
            highway_type = highway_type[0]
        
        if highway_type in highway_speeds:
            data['speed'] = highway_speeds[highway_type]
        else:
            data['speed'] = 30  # velocidade padrão

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
    m = folium.Map(location=start_location, zoom_start=16, tiles='OpenStreetMap')

    # Rota mais curta (azul)
    shortest_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]
    folium.PolyLine(
        locations=shortest_coords, 
        color='blue', 
        weight=6, 
        opacity=0.8,
        popup=folium.Popup('🔵 Rota mais curta (menor distância)', max_width=200),
        tooltip='Rota mais curta'
    ).add_to(m)

    # Rota mais rápida (vermelha)
    fastest_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in fastest_path]
    folium.PolyLine(
        locations=fastest_coords, 
        color='red', 
        weight=6, 
        opacity=0.8,
        popup=folium.Popup('🔴 Rota mais rápida (menor tempo)', max_width=200),
        tooltip='Rota mais rápida'
    ).add_to(m)

    # Adiciona marcadores de início e fim 
    end_node = shortest_path[-1]
    end_location = (graph.nodes[end_node]['y'], graph.nodes[end_node]['x'])
    
    folium.Marker(
        location=start_location, 
        popup=folium.Popup('🟢 Ponto de Partida', max_width=150),
        tooltip='Início da rota',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    folium.Marker(
        location=end_location, 
        popup=folium.Popup('🟠 Ponto de Destino', max_width=150),
        tooltip='Fim da rota',
        icon=folium.Icon(color='orange', icon='stop', prefix='fa')
    ).add_to(m)

    # Adiciona uma legenda HTML personalizada
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 220px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
    <h4 style="margin-top:0; color: #333;">🗺️ Legenda das Rotas</h4>
    <p style="margin: 5px 0;"><span style="color:blue; font-weight:bold;">━━━</span> Rota mais curta (distância)</p>
    <p style="margin: 5px 0;"><span style="color:red; font-weight:bold;">━━━</span> Rota mais rápida (tempo)</p>
    <p style="margin: 5px 0;">🟢 Início &nbsp;&nbsp;&nbsp; 🟠 Destino</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Ajusta o zoom para que toda a rota apareça na tela
    all_coords = shortest_coords + fastest_coords
    m.fit_bounds(all_coords)

    # Salva o mapa
    m.save('rotas.html')
    print("Mapa salvo como 'rotas.html'. Abra este arquivo no seu navegador.")

def main():
    # nome do lugar para baixar o mapa
    place_name = "Tamandaré, Pernambuco, Brazil"

    print(f"Baixando mapa de: {place_name}")
    # O network_type pode ser 'drive', 'walk', 'bike', 'all', etc. Define o tipo de rotas a incluir. drive = estradas para carros
    graph = ox.graph_from_place(place_name, network_type="drive")
    print("Mapa baixado com sucesso!")

    # Define as velocidades nas arestas
    set_edge_speed(graph)

    nodes_list = list(graph.nodes)
    start_node = nodes_list[0]  # Pega o primeiro nó da lista
    end_node = nodes_list[-1]   # Pega o último nó da lista
    print(f"Nós de início e fim: {start_node}, {end_node}")
    
    # Calcula a rota mais curta
    print(f"\nCalculando a rota mais CURTA de {start_node} para {end_node}...")
    shortest_path, shortest_cost = dijkstra(graph, start_node, end_node, weight_type='length')
    
    # Calcula a rota mais rápida
    print(f"Calculando a rota mais RÁPIDA de {start_node} para {end_node}...")
    fastest_path, fastest_cost = dijkstra(graph, start_node, end_node, weight_type='speed')
    
    if shortest_path and shortest_cost < float('inf'):
        print(f"\n✅ Rota mais CURTA encontrada com {len(shortest_path)} nós.")
        print(f"📏 Custo total (distância): {shortest_cost:.2f} metros ({shortest_cost/1000:.2f} km)")
        
        if fastest_path and fastest_cost < float('inf'):
            print(f"\n✅ Rota mais RÁPIDA encontrada com {len(fastest_path)} nós.")
            minutes = fastest_cost / 60
            print(f"⏱️ Custo total (tempo): {fastest_cost:.2f} segundos ({minutes:.2f} minutos)")
            
            # Compara as rotas
            if len(shortest_path) == len(fastest_path) and shortest_path == fastest_path:
                print("\n🔄 As rotas são idênticas!")
            else:
                print(f"\n📊 Comparação:")
                print(f"   • Diferença de nós: {abs(len(shortest_path) - len(fastest_path))} nós")
                distance_diff = abs(shortest_cost - (fastest_cost * 30 * 1000/3600))  # aproximação
                print(f"   • As rotas são diferentes")
            
            plot_route_on_map(graph, shortest_path, fastest_path)
        else:
            print("❌ Nenhuma rota rápida encontrada.")
            plot_route_on_map(graph, shortest_path, shortest_path)
    else:
        print("❌ Nenhum caminho encontrado entre os nós especificados.")

if __name__ == "__main__":
    main()