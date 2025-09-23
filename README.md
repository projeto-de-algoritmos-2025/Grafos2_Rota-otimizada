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

<img width="1280" height="663" alt="image" src="https://github.com/user-attachments/assets/70cf7209-edc1-4913-9ba4-d10dbfa8c58d" />


## Linguagem e Bibliotecas

* **Linguagem**: Python
* **Bibliotecas utilizadas**: Heapq ,folium, networkx, osmnx, streamlit

## Apresentação

A apresentação do projeto pode ser acessada [aqui](https://www.youtube.com/watch?v=C614gKM6kvs).

## Guia de Instalação

### Pré-requisitos

- Git;
- Python;
- Streamlit;
- Bibliotecas apresentadas em [requirements.txt](https://github.com/projeto-de-algoritmos-2025/Grafos2_Rota-otimizada/blob/main/requirements.txt).

### Executando o projeto

- Para executar o projeto localmente, basta clonar o repositório e instalar as dependências disponíveis em [requirements.txt](https://github.com/projeto-de-algoritmos-2025/Grafos2_Rota-otimizada/blob/main/requirements.txt). com `pip install -r requirements.txt`.

```bash
- Após isso, acesse a pasta `src` e execute o comando a seguir:

```bash
streamlit run app.py
```
