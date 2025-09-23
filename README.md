# Rota Mais Rápida vs Rota Mais Curta

**Conteúdo da Disciplina**: Grafos 2

## Alunos

<table>
  <tr>
    <td align="center"><a href="https://github.com/luanasoares0901"><img style="border-radius: 60%;" src="https://github.com/luanasoares0901.png" width="200px;" alt=""/><br /><sub><b>Luana Ribeiro</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/MMcLovin"><img style="border-radius: 60%;" src="https://github.com/MMcLovin.png" width="200px;" alt=""/><br /><sub><b>Gabriel Fernando de Jesus Silva</b></sub></a><br /></td>
  </tr>
</table>

## Sobre

Este projeto tem como objetivo desenvolver uma aplicação interativa que visualize e compare diferentes rotas entre dois pontos em uma área urbana. O resultado dessa comparação se dá apresentando o caminho mais curto e o mais rápido entre esses pontos, onde o mais curto utiliza-se da menor distância entre as arestas e o mais rápido utiliza a velocidade da via (considerada como o peso das arestas) para realizar a análise. Dessa forma, para a implementação foi utilizado o algoritmo de Dijkstra para calcular a rota mais curta e uma adaptação do mesmo algoritmo para encontrar a rota mais rápida, demonstrando a versatilidade de algoritmos de busca em grafos.

### Exemplo de rota gerada com o nosso algoritmo

![rota1](/assets/roto%20com%20o%20nosso%20algoritmo.png)

### Mesma rota usando o google maps

> A diferença do tempo se dá principalmente pelas velocidades (pesos das arestas) que escolhemos usar para cada tipo de rua.

![rota2](/assets/rota%20google%20maps.png)

## Linguagem e Bibliotecas

* **Linguagem**: Python
* **Principais Bibliotecas utilizadas**: Heapq (nativa do python para utilização de minHeaps), folium (para visualização de mapas), networkx (para manipulação de grafos), osmnx (para obtenção dos dados de mapas pelo [OpenStreetMaps](https://www.openstreetmap.org/#map=4/-15.41/-53.70)) e streamlit (para criação de interfaces web interativas)

## Apresentação

A apresentação do projeto pode ser acessada [aqui](https://www.youtube.com/watch?v=C614gKM6kvs).

## Guia de Instalação

### Pré-requisitos

- Git (versão 2.40 ou superior);
- Python (versão 3.11 ou superior);

### Executando o projeto

- Recomendamos criar um ambiente virtual para o projeto. Para isso, utilize os comandos abaixo:

```bash
python -m venv env
source env/bin/activate  # No Windows use: env\Scripts\activate
```

- Em seguida, instale as dependências disponíveis em [requirements.txt](https://github.com/projeto-de-algoritmos-2025/Grafos2_Rota-otimizada/blob/main/requirements.txt):

```bash
pip install -r requirements.txt
```

- Após instalar as dependências, acesse a pasta `src` e execute o comando:

```bash
streamlit run app.py
```
