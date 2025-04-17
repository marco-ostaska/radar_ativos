import os
import json
import datetime
import streamlit as st
import yaml
import requests
from pathlib import Path

import streamlit_core.acoes_st as acoes_st
import streamlit_core.fii_st as fii_st
from modules.ativosYAML import montar_add, montar_remove

# st.set_page_config(layout="wide")

API_URL = "http://localhost:8000"  # ajuste se necessário

def get_indices():
    try:
        response = requests.get(f"{API_URL}/indices")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter índices: {str(e)}")
        return {
            'selic': 0, 'ipca': 0,
            'selic_atual': 0, 'ipca_media5': 0, 'ipca_atual': 0
        }

def melhor_indice():
    indices = get_indices()
    return max(indices['selic'], indices['ipca'])

def compare_status(compare1, compare2, text):
    if compare1 is None or compare2 is None:
        return
    if compare1 > compare2:
        st.success(f"{text}")
    elif compare1 == compare2:
        st.warning(f"{text}")
    else:
        st.error(f"{text}")

def fmt_radar_head(tipo):
    col = st.columns(10) if tipo == "acoes" else st.columns(9)
    labels = ["Ativo:", "Cotação:",
              "cotação x lucro:" if tipo == "acoes" else "Valor Patrimonial:",
              "Valor Teto por DY:", "DY:", "Rendimento Real:", "Potencial:"]

    for i, label in enumerate(labels):
        with col[i]:
            st.markdown(f"**{label}**")

    if tipo == "acoes":
        with col[7]: st.markdown("**Earning Yield:**")
        with col[8]: st.markdown("**Nota Risco:**")
        with col[9]: st.markdown("**Score:**")
    else:
        with col[7]: st.markdown("**Nota Risco:**")
        with col[8]: st.markdown("**Score:**")

def fmt_radar_fii(tipo, data, indice_base, indices):
    fmt_radar_head("fii")
    for ticker in data[tipo]["tickers"]:
        ticker_code = ticker['ticker']
        try:
            r = requests.get(f"{API_URL}/fii/radar", params={"ticker": ticker_code, "tipo": tipo})
            r.raise_for_status()
            fi = r.json()
        except Exception as e:
            st.error(f"Erro em {ticker_code}: {e}")
            continue

        col = st.columns(9)
        with col[0]: st.info(fi['ticker'])
        with col[1]: st.info(f"R$ {fi['cotacao']}")
        with col[2]: compare_status(fi['vpa'], fi['cotacao'], f"R$ {fi['vpa']}")
        with col[3]: compare_status(fi['teto_div'], fi['cotacao'], f"R$ {fi['teto_div']:.2f}")
        with col[4]: compare_status(fi['dy_estimado'], data[tipo]['spread'] + indice_base, f"{fi['dy_estimado']:.2f}%")
        with col[5]: compare_status(fi['rendimento_real'], max(indices['ipca_atual'], (indices['selic_atual'] - indices['selic_atual'] * 0.15) - indices['ipca_atual']), f"{fi['rendimento_real']:.2f}%")
        with col[6]: compare_status(fi['potencial'], 0, f"{fi['potencial']}%")
        with col[7]: compare_status(fi['nota_risco'], 5, f"{fi['nota_risco']}")
        with col[8]: compare_status(fi['score'], 6, f"{fi['score']}")

def fmt_radar_acoes(tipo, data, indice_base, indices):
    fmt_radar_head("acoes")
    for ticker in data[tipo]["tickers"]:
        ticker_code = ticker['ticker']
        try:
            r = requests.get(f"{API_URL}/acoes/radar", params={"ticker": ticker_code})
            r.raise_for_status()
            ac = r.json()
        except Exception as e:
            st.error(f"Erro em {ticker_code}: {e}")
            continue

        col = st.columns(10)
        with col[0]: st.info(ac['ticker'])
        with col[1]: st.info(f"R$ {ac['cotacao']}")
        with col[2]: compare_status(ac['teto_por_lucro'], ac['cotacao'], f"R$ {ac['teto_por_lucro']}")
        with col[3]: compare_status(ac['valor_teto_por_dy'], ac['cotacao'], f"R$ {ac['valor_teto_por_dy']}")
        with col[4]: compare_status(ac['dy_estimado'], indice_base, f"{ac['dy_estimado']:.2f}%")
        with col[5]: compare_status(ac['rendimento_real'], max(indices['ipca_atual'], (indices['selic_atual'] - indices['selic_atual'] * 0.15) - indices['ipca_atual']), f"{ac['rendimento_real']:.2f}%")
        with col[6]: compare_status(ac['potencial'], 0, f"{ac['potencial']}%")
        with col[7]: compare_status(ac['earning_yield'], indice_base, f"{ac['earning_yield']:.2f}%")
        with col[8]: compare_status(ac['nota_risco'], 5, f"{ac['nota_risco']}")
        with col[9]: compare_status(ac['score'], 5, f"{ac['score']}")

def fmt_radar_indice(indices):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('**Indice**')
    with col2: st.markdown('**Atual**')
    with col3: st.markdown('**Média 5 Anos**')
    with col4: st.markdown('**Juros Real**')

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.info("SELIC")
    with col2: st.info(f"{indices['selic_atual']}%")
    with col3: st.info(f"{indices['selic']}%")
    with col4: st.info(f"{round((indices['selic_atual'] - indices['selic_atual'] * 0.15) - indices['ipca_atual'], 2)}%")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.info("IPCA")
    with col2: st.info(f"{indices['ipca_atual']}%")
    with col3: st.info(f"{indices['ipca_media5']}%")
    with col4: st.info("N/A")

def radar(indice_base):
    indices = get_indices()
    if st.button("Atualizar Indices"):
        with st.spinner("Atualizando dados..."):
            indices = get_indices()
        st.success("Dados atualizados com sucesso!")
    fmt_radar_indice(indices)

    sl = st.selectbox("Selecione o tipo de ativo", ["", "FII", "Ações"])
    base_dir = Path(__file__).resolve().parents[2]
    ativo_arq = base_dir / 'data' / 'ativos.yml'
    with open(ativo_arq, 'r') as file:
        data = yaml.safe_load(file)

    st.title("Radar de Ativos")
    if sl == "FII":
        for tipo in ["shopping", "logistica", "papel", "hibrido", "fiagro", "infra"]:
            st.subheader(tipo.upper())
            fmt_radar_fii(tipo, data, indice_base, indices)
    if sl == "Ações":
        st.markdown("---")
        st.subheader("Ações")
        fmt_radar_acoes("acoes", data, indice_base, indices)

def iniciar():
    indice_base = melhor_indice()
    st.sidebar.title("Consulta de Ativos")
    chk_radio = st.sidebar.radio("Selecione o tipo de ativo", ["FII", "Ações"], index=0)
    if ticker := st.sidebar.text_input('Digite o ticker do FII', help="Exemplo: HGLG11"):
        if chk_radio == "FII":
            fii_st.processar(ticker, indice_base)
        if chk_radio == "Ações":
            acoes_st.processar(ticker, indice_base)
    else:
        st.sidebar.warning("Por favor, insira o ticker de um FII para obter as informações.")
        radar(indice_base)

    st.sidebar.markdown("---")
    st.sidebar.title("Configurações")
    cfg = st.sidebar.selectbox("Selecione a opção", ["", "Adicionar Ativos", "Remover Ativos"], index=0)
    if cfg == "Adicionar Ativos":
        montar_add()
    elif cfg == "Remover Ativos":
        montar_remove()

if __name__ == "__main__":
    iniciar()
