import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import heapq
import pprint
from heapdict import heapdict
import folium
import streamlit as st
from streamlit_folium import st_folium

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
    # TODO: comparar o tempo de execução usando heapq vs heapdict

    # para simularmos a heap do jeito que aprendemos, precisamos usar 2 estruturas de dados, uma para o atual custo e outra para saber a ordem minHeap
    cheapest_path = {node: float('inf') for node in graph.nodes}
    cheapest_path[start_node] = 0
    fastest_path_length = 0

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
                speed = data.get('speed', 20)   # velocidade em km/h
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

    return predecessors, path, cheapest_path[end_node]

def set_edge_speed():
    """
    Adiciona um atributo 'speed' às arestas do grafo com base no tipo de via e atribui valores de velocidade.
    """

    graph = st.session_state.graph

    # inicializa todas as velocidades como 10 km/h (padrão)
    nx.set_edge_attributes(graph, 10, name="speed")

    highway_speeds = {
        'secondary_link': 60,
        'primary_link': 70,
        'path': 5,
        'pedestrian': 5,
        'tertiary': 50,
        'unclassified': 10,
        'service': 15,
        'primary': 70,
        'secondary': 60,
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
    fig, ax = ox.plot_graph(graph, node_size=0, edge_color="gray", edge_linewidth=0.5)
    plt.show()

def plot_route_on_map(graph, shortest_path, fastest_path, attrs):
    # Pegando as coordenadas do ponto de partida para centralizar o mapa
    start_node = shortest_path[0]
    start_location = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])

    # Cria um mapa Folium manualmente, centrado no ponto de partida
    m = folium.Map(location=start_location, zoom_start=16, attr=attrs["attr"], tiles=attrs["tiles"])

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

    # Adicionando marcadores de início e fim 
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
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                color: black;">
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

    return m

@st.cache_data
def get_graph(place_name):
    """
    Baixa o grafo da cidade e o armazena em cache para não baixar novamente.
    """
    try:
        graph = ox.graph_from_place(place_name, network_type="drive")
        return graph
    except Exception as e:
        st.error(f"Não foi possível baixar o mapa para '{place_name}'. Verifique o nome do lugar.")
        st.error(f"Erro: {e}")
        return None

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if "place_name" not in st.session_state:
        st.session_state.place_name = "Tamandaré, Pernambuco, Brazil"
    if "start_point" not in st.session_state:
        st.session_state.start_point = None
        st.session_state.end_point = None
        st.session_state.route_map = None
        st.session_state.shortest_path = None
        st.session_state.fastest_path = None
        st.session_state.last_click = None
        st.session_state.zoom_level = None
        st.session_state.graph = None
        st.session_state.last_loaded_place = None

def render_sidebar():
    """Cria e gerencia o painel lateral da aplicação."""
    with st.sidebar:
        st.header("Configurações")
        
        # Usa uma chave para que o st.text_input atualize o st.session_state.place_name
        st.session_state.place_name = st.text_input(
            "Digite o nome da cidade",
            st.session_state.place_name,
            key="place_input"
        )
        
        st.info("Clique no mapa para definir os pontos de partida e chegada.")

        st.write(f"📍 **Partida:** {'Selecionada' if st.session_state.start_point else 'Não selecionada'}")
        if st.session_state.start_point:
            st.write(f"  > Lat: {st.session_state.start_point['lat']:.5f}, Lng: {st.session_state.start_point['lng']:.5f}")

        st.write(f"🏁 **Chegada:** {'Selecionada' if st.session_state.end_point else 'Não selecionada'}")
        if st.session_state.end_point:
            st.write(f"  > Lat: {st.session_state.end_point['lat']:.5f}, Lng: {st.session_state.end_point['lng']:.5f}")

        calculate_button = st.button(
            "Calcular Rota",
            type="primary",
            disabled=(st.session_state.start_point is None or st.session_state.end_point is None or st.session_state.graph is None)
        )

        if calculate_button:
            calculate_route()

        if st.button("Limpar Pontos"):
            clear_points()
            st.rerun()

def get_route_names(graph, route):
    """
    Retorna uma string com o nome das ruas da rota, tratando casos onde
    o nome é uma lista de strings.
    """
    route_names = []
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i+1]
        
        # Acessa os dados da aresta entre os nós u e v
        # O argumento keys=True é necessário para grafos multi-aresta
        edge_data = graph.get_edge_data(u, v, key=0)

        if edge_data:
            # Pega o valor do atributo 'name', com um fallback se não existir
            edge_name = edge_data.get('name')

            # Trata o caso onde o 'name' é uma lista ou uma string
            if isinstance(edge_name, list):
                # Se for uma lista, pegue o primeiro nome
                current_name = edge_name[0]
            elif isinstance(edge_name, str):
                # Se for uma string, use-a diretamente
                current_name = edge_name
            else:
                # Se não houver nome, use um fallback
                current_name = 'Sem nome'

            # Adiciona o nome à lista, evitando duplicatas consecutivas
            if not route_names or route_names[-1] != current_name:
                route_names.append(current_name)
    
    # Junta os nomes das ruas em uma única string
    return "  ➡️  ".join(route_names)

def compare_routes(shortest, fastest):
    # Calcular e exibir a distância da rota mais curta (já está no 'cost' de dijkstra)
    st.success(f"Rota mais ***curta*** encontrada com {len(shortest['path'])} nós!")
    st.metric(label="Distância Total", value=f"{shortest['cost']/1000:.2f} km")

    # Calcular o tempo total de viagem da rota mais curta
    total_time_shortest_route = 0
    graph = st.session_state.graph

    for i in range(len(shortest['path']) - 1):
        u = shortest['path'][i]
        v = shortest['path'][i+1]
        
        edge_data = graph.get_edge_data(u, v, key=0)

        if edge_data and 'length' in edge_data and 'speed' in edge_data:
            length = edge_data['length']
            speed = edge_data['speed']
            
            # Converter a velocidade de km/h para m/s
            speed_ms = speed * (1000 / 3600)
            
            # Calcular o tempo de viagem e somar ao total
            if speed_ms > 0:
                total_time_shortest_route += length / speed_ms

    st.metric(label="Tempo Total de Viagem", value=f"{total_time_shortest_route/60:.2f} minutos")

    st.write("---") # Linha divisória para melhor visualização

    # Calcular a distância total da rota mais rápida (implementação já feita)
    total_length_fastest_route = 0
    
    for i in range(len(fastest['path']) - 1):
        u = fastest['path'][i]
        v = fastest['path'][i+1]
        
        edge_data = graph.get_edge_data(u, v, key=0)
        
        if edge_data and 'length' in edge_data:
            total_length_fastest_route += edge_data['length']

    # Exibir a distância e o tempo da rota mais rápida
    st.success(f"Rota mais ***rápida*** encontrada com {len(fastest['path'])} nós!")
    st.metric(label="Distância Total", value=f"{total_length_fastest_route/1000:.2f} km")
    st.metric(label="Tempo Total de Viagem", value=f"{fastest['cost']/60:.2f} minutos")

def calculate_route():
    """Lógica para calcular e plotar a rota."""
    if st.session_state.graph:
        with st.spinner("Calculando a rota..."):
            start_coords = (st.session_state.start_point['lat'], st.session_state.start_point['lng'])
            end_coords = (st.session_state.end_point['lat'], st.session_state.end_point['lng'])

            start_node = ox.distance.nearest_nodes(st.session_state.graph, X=start_coords[1], Y=start_coords[0])
            end_node = ox.distance.nearest_nodes(st.session_state.graph, X=end_coords[1], Y=end_coords[0])

            shortest = {
                "predecessors": None,
                "path": None,
                "cost": None
            }
            shortest["predecessors"], shortest["path"], shortest["cost"] = dijkstra(st.session_state.graph, start_node, end_node, 'length')

            fastest = {
                "predecessors": None,
                "path": None,
                "cost": None
            }
            fastest["predecessors"], fastest["path"], fastest["cost"] = dijkstra(st.session_state.graph, start_node, end_node, 'speed')

            if shortest["path"] and fastest["path"]:

                compare_routes(shortest, fastest)


                st.session_state.route_map = plot_route_on_map(
                    st.session_state.graph, 
                    shortest["path"], 
                    fastest["path"],
                    {"attr": st.session_state.attr, "tiles": st.session_state.tiles}
                )
                st.session_state.shortest_path = shortest["path"]
                st.session_state.fastest_path = fastest["path"]
            else:
                st.error("Não foi possível encontrar um caminho.")
                st.session_state.route_map = None

def clear_points():
    """Limpa os pontos de início e fim do estado da sessão."""
    st.session_state.start_point = None
    st.session_state.end_point = None
    st.session_state.route_map = None
    st.session_state.last_click = None
    st.session_state.shortest_path = None

def render_map():
    """Renderiza o mapa principal e gerencia a lógica de cliques."""
    if st.session_state.graph:
        if st.session_state.route_map:
            # Exibe o mapa com a rota calculada
            st_folium(st.session_state.route_map, width='100%', height=500, returned_objects=[])
        else:
            # Exibe o mapa para seleção de pontos
            avg_y = sum(d['y'] for n, d in st.session_state.graph.nodes(data=True)) / len(st.session_state.graph.nodes)
            avg_x = sum(d['x'] for n, d in st.session_state.graph.nodes(data=True)) / len(st.session_state.graph.nodes)

            m = folium.Map(location=[avg_y, avg_x], zoom_start=14, tiles=st.session_state.tiles, attr=st.session_state.attr)

            if st.session_state.start_point:
                folium.Marker(
                    location=[st.session_state.start_point['lat'], st.session_state.start_point['lng']],
                    popup='Ponto de Partida', icon=folium.Icon(color='green')
                ).add_to(m)
            if st.session_state.end_point:
                folium.Marker(
                    location=[st.session_state.end_point['lat'], st.session_state.end_point['lng']],
                    popup='Ponto de Chegada', icon=folium.Icon(color='red')
                ).add_to(m)

            map_data = st_folium(m, width='100%', height=500, returned_objects=['last_clicked', 'zoom'])

            if map_data and map_data["last_clicked"] and map_data["last_clicked"] != st.session_state.last_click:
                st.session_state.last_click = map_data["last_clicked"]
                if st.session_state.start_point is None:
                    st.session_state.start_point = map_data["last_clicked"]
                elif st.session_state.end_point is None:
                    st.session_state.end_point = map_data["last_clicked"]
                st.session_state.zoom_level = map_data['zoom']
                st.rerun()

def render_route_path():
    """Exibe o caminho da rota na interface."""
    shortest_path = st.session_state.get("shortest_path")
    fastest_path = st.session_state.get("fastest_path")
    if fastest_path and shortest_path and st.session_state.graph:
        route_names = get_route_names(st.session_state.graph, shortest_path)
        st.info(f"📏 **Caminho da Rota mais curta:**\n\n{route_names}")

        route_names = get_route_names(st.session_state.graph, fastest_path)
        st.info(f"🚀 **Caminho da Rota mais rápida:**\n\n{route_names}")

def main():
    """Função principal que orquestra a aplicação Streamlit."""
    st.set_page_config(page_title="Calculadora de Rotas", layout="wide")
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            width: 400px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("🗺️ Calculando Rotas Mais Eficientes")

    initialize_session_state()

    # Centralize o carregamento do grafo aqui
    # Se o nome da cidade no input mudou, recarregue o grafo
    if st.session_state.place_name != st.session_state.last_loaded_place:
        with st.spinner(f"Carregando o mapa para {st.session_state.place_name}..."):
            st.session_state.graph = get_graph(st.session_state.place_name)
            st.session_state.last_loaded_place = st.session_state.place_name
            clear_points() # Limpa os pontos antigos para a nova cidade
            st.rerun()

    st.session_state.tiles = "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png"
    st.session_state.attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles courtesy of <a href="http://www.openstreetmap.bzh/" target="_blank">Breton OpenStreetMap Team</a>'

    set_edge_speed()
    render_sidebar()
    render_route_path()
    render_map()

if __name__ == "__main__":
    main()