import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd
import heapq

st.set_page_config(layout="wide")
st.title("JLR - Otimizador de Rota para AGV ")

# -----------------------------
# Parâmetros fixos
# -----------------------------
VELOCIDADE_AGV = 0.1  # metros por segundo

# -----------------------------
# Grafo Direcionado (Sem Ré)
# -----------------------------
grafo = {
    'P0': ['P1', 'P27'],
    'P1': ['P2'],
    'P2': ['P3'],
    'P3': ['P4'],
    'P4': ['P5'],
    'P5': ['P6'],
    'P6': ['P7'],
    'P7': ['P8'],
    'P8': ['P9', 'P15'],
    'P9': ['P10'],
    'P10': ['P12'],
    'P12': ['P13'],
    'P13': ['P14'],
    'P14': ['P38', 'P26', 'P27'],
    'P38': ['P37'],
    'P37': ['P36'],
    'P36': ['P35'],
    'P35': ['P34'],
    'P34': ['P33'],
    'P33': ['P32'],
    'P32': ['P31'],
    'P31': ['P30'],
    'P30': ['P29'],
    'P29': ['P28'],
    'P28': ['P27'],
    'P27': ['P0'],  # caminho válido de volta ao P0
    'P15': ['P16'],
    'P16': ['P17'],
    'P17': ['P18'],
    'P18': ['P19'],
    'P19': ['P20'],
    'P20': ['P21'],
    'P21': ['P22'],
    'P22': ['P23'],
    'P23': ['P24'],
    'P24': ['P25'],
    'P25': ['P26'],
    'P26': ['P27']
}

# -----------------------------
# Coordenadas Reais dos Pontos
# -----------------------------
coordenadas_reais = {
    'P0': (845, 44), 'P1': (764, 128), 'P2': (664, 128), 'P3': (564, 128), 'P4': (464, 128),
    'P5': (364, 128), 'P6': (264, 128), 'P7': (264, 180), 'P8': (264, 255), 'P9': (382, 255),
    'P10': (473, 255), 'P12': (552, 255), 'P13': (658, 255), 'P14': (765, 255), 'P15': (264, 320),
    'P16': (264, 397), 'P17': (264, 473), 'P18': (364, 473), 'P19': (464, 473), 'P20': (564, 473),
    'P21': (664, 473), 'P22': (764, 473), 'P23': (864, 473), 'P24': (964, 473), 'P25': (936, 392),
    'P26': (946, 320), 'P27': (934, 128), 'P28': (1069, 128), 'P29': (1142, 128), 'P30': (1213, 128),
    'P31': (1282, 128), 'P32': (1370, 128), 'P33': (1474, 180), 'P34': (1366, 255), 'P35': (1282, 255),
    'P36': (1212, 255), 'P37': (1136, 255), 'P38': (1062, 255),
}

pontos_dict = {k: np.array(v) for k, v in coordenadas_reais.items()}
nomes_pontos = list(coordenadas_reais.keys())

# -----------------------------
# Interface do usuário
# -----------------------------
postos_nomes = st.multiselect(
    "🍣 Selecione os Postos de Abastecimento (AGV parte e retorna do P0):",
    nomes_pontos[1:],
    default=["P1", "P2", "P5"]
)

prioridade_nomes = st.multiselect(
    "⬆️ Defina a prioridade de visita (em ordem, opcional):",
    postos_nomes,
    default=[]
)

tempo_medio = st.number_input(
    "⏱️ Tempo médio por estação (em minutos):",
    min_value=0.0,
    value=2.0,
    step=0.5
)

# -----------------------------
# Algoritmo de Dijkstra
# -----------------------------
def dijkstra(grafo, pontos_dict, inicio, fim):
    fila = [(0, inicio, [inicio])]
    visitados = set()
    while fila:
        (custo, atual, caminho) = heapq.heappop(fila)
        if atual in visitados:
            continue
        if atual == fim:
            return caminho, custo
        visitados.add(atual)
        for vizinho in grafo.get(atual, []):
            if vizinho not in visitados:
                novo_caminho = caminho + [vizinho]
                dist = np.linalg.norm(pontos_dict[atual] - pontos_dict[vizinho])
                heapq.heappush(fila, (custo + dist, vizinho, novo_caminho))
    return None, float('inf')

# -----------------------------
# Cálculo da melhor rota
# -----------------------------
def calcular_rota_caminho(ordem):
    caminho_total = []
    distancia_total = 0
    for i in range(len(ordem) - 1):
        trecho, dist = dijkstra(grafo, pontos_dict, ordem[i], ordem[i + 1])
        if trecho is None:
            return [], float('inf')
        if i > 0:
            trecho = trecho[1:]  # evitar repetição
        caminho_total += trecho
        distancia_total += dist
    return caminho_total, distancia_total

if postos_nomes:
    base_rota = postos_nomes.copy()
    if prioridade_nomes:
        for nome in prioridade_nomes:
            base_rota.remove(nome)
        base_rota = prioridade_nomes + base_rota

    melhores = []
    for _ in range(200):
        meio = base_rota[len(prioridade_nomes):]
        random.shuffle(meio)
        tentativa = prioridade_nomes + meio
        ordem = ['P0'] + tentativa + ['P0']
        caminho, dist = calcular_rota_caminho(ordem)
        tempo_min = (dist / VELOCIDADE_AGV) / 60 + tempo_medio * len(tentativa)
        melhores.append((tempo_min, dist, ordem, caminho))

    melhores.sort()
    top5 = melhores[:5]

    st.subheader("🏆 Tabela com as 5 melhores rotas")
    dados_resultados = []
    for i, (tempo_min, dist, ordem, caminho) in enumerate(top5):
        dados_resultados.append({
            "Ranking": f"#{i+1}",
            "Sequência": " → ".join(ordem),
            "Distância (m)": round(dist, 2),
            "Deslocamento (min)": round((dist / VELOCIDADE_AGV) / 60, 2),
            "Tempo Total (min)": round(tempo_min, 2),
        })

    st.dataframe(dados_resultados, use_container_width=True)

    melhor = top5[0]
    coords = np.array([pontos_dict[p] for p in melhor[3]])

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Rota Otimizada do AGV")
    ax.set_xlim(0, 1600)
    ax.set_ylim(600, 0)
    ax.plot(coords[:, 0], coords[:, 1], 'o-', color='red', label='Melhor Rota')

    ax.plot(pontos_dict['P0'][0], pontos_dict['P0'][1], 'bs', label='P0 (Base)')
    for nome, (x, y) in pontos_dict.items():
        cor = "red" if nome in postos_nomes else ("blue" if nome == 'P0' else "gray")
        ax.plot(x, y, 'o', color=cor)
        ax.text(x + 5, y + 5, nome, fontsize=8)

    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    st.subheader("📍 Melhor Sequência Otimizada de Paradas")
    st.code(" → ".join(melhor[2]))

    st.success(f"📏 Distância: {round(melhor[1], 2)} m")
    st.info(f"🚚 Deslocamento: {round((melhor[1] / VELOCIDADE_AGV) / 60, 2)} min")
    st.warning(f"⏱️ Tempo Total Estimado: {round(melhor[0], 2)} min")
