import streamlit as st
import networkx as nx
import time
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Rota AGV", layout="wide")

# --- Criando um grafo de exemplo com coordenadas
G = nx.DiGraph()

nodes = {
    "P0": (0, 0), "P1": (1, 0), "P2": (2, 0), "P3": (3, 0),
    "P4": (0, 1), "P5": (1, 1), "P6": (2, 1), "P7": (3, 1),
    "P8": (0, 2), "P9": (1, 2), "P10": (2, 2), "P11": (3, 2)
}

edges = [
    ("P0", "P1"), ("P1", "P2"), ("P2", "P3"),
    ("P4", "P5"), ("P5", "P6"), ("P6", "P7"),
    ("P8", "P9"), ("P9", "P10"), ("P10", "P11"),
    ("P0", "P4"), ("P4", "P8"),
    ("P1", "P5"), ("P5", "P9"),
    ("P2", "P6"), ("P6", "P10"),
    ("P3", "P7"), ("P7", "P11")
]

for node, pos in nodes.items():
    G.add_node(node, pos=pos)

for u, v in edges:
    G.add_edge(u, v, weight=1)

# --- Interface Streamlit
st.title("🚗 Simulador de Rota para AGV")

col1, col2 = st.columns(2)
with col1:
    origem = st.selectbox("Ponto de origem", list(nodes.keys()))
with col2:
    destino = st.selectbox("Ponto de destino", list(nodes.keys()))

start_simulation = st.button("Iniciar Simulação")

# --- Calcular rota
if start_simulation:
    if origem == destino:
        st.warning("Origem e destino são iguais!")
    else:
        try:
            path = nx.dijkstra_path(G, origem, destino)
            st.success(f"Rota encontrada: {' → '.join(path)}")

            # --- Animação da movimentação
            placeholder = st.empty()
            for i, ponto in enumerate(path):
                fig, ax = plt.subplots()
                nx.draw(G, pos=nodes, with_labels=True, node_size=500,
                        node_color=['red' if n == ponto else 'lightblue' for n in G.nodes()],
                        edge_color='gray', ax=ax)
                ax.set_title(f"Movendo para: {ponto}")
                ax.set_xlim(-1, 4)
                ax.set_ylim(-1, 3)
                ax.grid(True)
                placeholder.pyplot(fig)
                time.sleep(1)

            st.balloons()
        except nx.NetworkXNoPath:
            st.error("Não foi possível encontrar um caminho.")
