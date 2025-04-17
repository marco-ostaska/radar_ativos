import streamlit as st
import requests
from modules.scoreFII import evaluate_fii

API_URL = "http://localhost:8000"

def compare_status(compare1, compare2, text):
    if compare1 is None or compare2 is None:
        return
    if compare1 > compare2:
        st.success(f"{text}")
    elif compare1 == compare2:
        st.warning(f"{text}")
    else:
        st.error(f"{text}")

def format_millions_billions(value):
    if value is None:
        return
    if value >= 1e9:
        return "{:.2f}b".format(value / 1e9)
    elif value >= 1e6:
        return "{:.2f}M".format(value / 1e6)
    else:
        return "{:.2f}".format(value)

def processar(ticker, indice_base):
    try:
        response = requests.get(f"{API_URL}/fii/detalhado", params={"ticker": ticker, "tipo": "papel"})
        response.raise_for_status()
        fi = response.json()

        st.title(fi["ticker"])
        st.subheader("Fundo Imobiliário")
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        st.subheader("Informações Gerais")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('**Cotação:**')
            st.info(f"R$ {fi['cotacao']}")
        with col2:
            st.markdown('**DY (12M):**')
            st.info(f"{fi['dividend_yield']:.2f}%")
        with col3:
            st.markdown('**Nota:**')
            compare_status(fi['score'], 6, f"{fi['score']}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Informações sobre Valor Patrimonial")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Valor Patrimonial Por Cota:**')
            compare_status(fi['vpa'], fi['cotacao'], f"R$ {fi['vpa']}")
        with col2:
            st.markdown('**Número De Cotas:**')
            st.info(f"{format_millions_billions(fi['cotas_emitidas'])}")
        with col1:
            st.markdown('**P/VP:**')
            compare_status(1, fi['pvp'], f"{fi['pvp']}")
        with col2:
            st.markdown('**Valor Patrimonial:**')
            st.info(f"R$ {format_millions_billions(fi['valor_patrimonial'])}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Distribuições nos Últimos 12 Meses")
        col1, col2, col3, col4 = st.columns(4)
        for i, label in enumerate(["1 mes", "3 meses", "6 meses", "12 meses"]):
            with [col1, col2, col3, col4][i]:
                val = fi['historico_dividendos'][label]
                st.metric(label=f"Yield {label}", value=f"{(val / fi['cotacao']) * 100:.2f}%", delta=f"R$ {val:,.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Guia de Compras: Preço Teto, Yield Projetado")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Valor Patrimonial Por Cota:**')
            compare_status(fi['vpa'], fi['cotacao'], f"R$ {fi['vpa']}")
        with col2:
            st.markdown('**Yield estimado próximos 12m**')
            dy_est = (fi['dividendo_estimado'] / fi['cotacao']) * 100
            compare_status(dy_est, fi['dividend_yield'], f"{dy_est:.2f}%")

        with col1:
            st.markdown('**Dividendos Estimados próximos 12m:**')
            compare_status(fi['dividendo_estimado'], fi['historico_dividendos']['12 meses'], f"R$ {fi['dividendo_estimado']:,.2f}")
        with col2:
            st.markdown('**Dividendos Estimado por mês**')
            compare_status(fi['dividendo_estimado'] / 12, fi['historico_dividendos']['12 meses'] / 12, f"R$ {fi['dividendo_estimado'] / 12:,.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.text("Preço Teto baseado em dividendos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('**Tijolo**')
            compare_status(fi['dividendo_estimado'] / (indice_base + 3) * 100, fi['cotacao'], f"R$ {fi['dividendo_estimado'] / (indice_base + 3) * 100:.2f}")
        with col2:
            st.markdown('**Papel**')
            compare_status(fi['dividendo_estimado'] / (indice_base + 5) * 100, fi['cotacao'], f"R$ {fi['dividendo_estimado'] / (indice_base + 5) * 100:.2f}")
        with col3:
            st.markdown('**Infra ou Agro**')
            compare_status(fi['dividendo_estimado'] / (indice_base + 8) * 100, fi['cotacao'], f"R$ {fi['dividendo_estimado'] / (indice_base + 8) * 100:.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Necessário para R$1000 de rendimentos mensais")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Cotas Necessárias:**')
            st.info("{:,.0f}".format(fi['cotas_necessarias_para_1000_mensais']))
        with col2:
            st.markdown('**Investimento Necessário:**')
            st.info(f"R$ {fi['investimento_necessario_para_1000_mensais']:,.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o ticker: {str(e)}")
