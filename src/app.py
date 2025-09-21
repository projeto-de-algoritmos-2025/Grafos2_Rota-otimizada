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
    fig, ax = ox.plot_graph(graph, node_size=0, edge_color="gray", edge_linewidth=0.5)
    plt.show()

def plot_route_on_map(graph, shortest_path, attrs):
    # Pegando as coordenadas do ponto de partida para centralizar o mapa
    start_node = shortest_path[0]
    start_location = (graph.nodes[start_node]['y'], graph.nodes[start_node]['x'])

    # Cria um mapa Folium manualmente, centrado no ponto de partida
    m = folium.Map(location=start_location, zoom_start=16, attr=attrs["attr"], tiles=attrs["tiles"])

    # Criam uma lista de tuplas (latitude, longitude) para cada nó do caminho
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]

    # Usando a PolyLine pra desenhar uma linha conectando as coordenadas
    folium.PolyLine(locations=route_coords, color='blue', weight=5).add_to(m)

    # Adicionando marcadores de início e fim 
    end_node = shortest_path[-1]
    end_location = (graph.nodes[end_node]['y'], graph.nodes[end_node]['x'])
    folium.Marker(location=start_location, popup='Início', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=end_location, popup='Fim', icon=folium.Icon(color='red')).add_to(m)

    # Ajusta o zoom para que toda a rota apareça na tela
    m.fit_bounds(folium.PolyLine(locations=route_coords).get_bounds())

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

def calculate_route():
    """Lógica para calcular e plotar a rota."""
    if st.session_state.graph:
        with st.spinner("Calculando a rota..."):
            start_coords = (st.session_state.start_point['lat'], st.session_state.start_point['lng'])
            end_coords = (st.session_state.end_point['lat'], st.session_state.end_point['lng'])

            start_node = ox.distance.nearest_nodes(st.session_state.graph, X=start_coords[1], Y=start_coords[0])
            end_node = ox.distance.nearest_nodes(st.session_state.graph, X=end_coords[1], Y=end_coords[0])
            
            shortest_path, path_cost = dijkstra(st.session_state.graph, start_node, end_node, 'length')
            
            if shortest_path:
                st.success(f"Rota encontrada com {len(shortest_path)} nós!")
                st.metric(label="Distância Total", value=f"{path_cost:.2f} metros")

                st.session_state.route_map = plot_route_on_map(
                    st.session_state.graph, 
                    shortest_path, 
                    {"attr": st.session_state.attr, "tiles": st.session_state.tiles}
                )
                st.session_state.shortest_path = shortest_path
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
    if shortest_path and st.session_state.graph:
        # Chama a nova função para obter os nomes das ruas
        route_names = get_route_names(st.session_state.graph, shortest_path)
        st.info(f"🛣️ **Caminho da Rota:**\n\n{route_names}")

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

    render_sidebar()
    render_route_path()
    render_map()

if __name__ == "__main__":
    main()