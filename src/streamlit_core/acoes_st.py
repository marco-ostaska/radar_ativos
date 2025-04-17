import streamlit as st
import requests

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
        response = requests.get(f"{API_URL}/acoes/detalhado", params={"ticker": ticker})
        response.raise_for_status()
        ativo = response.json()

        st.title(ativo["ticker"])
        st.subheader("Ação")
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        st.subheader("Informações Gerais")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('**Cotação:**')
            st.info(f"R$ {ativo['cotacao']}")
        with col2:
            st.markdown('**DY (12M):**')
            compare_status(ativo['dy_estimado'] / 100, indice_base / 100, f"{ativo['dy_estimado']:.2f}%")
        with col3:
            st.markdown('**Nota:**')
            compare_status(ativo['score'], 5, f"{ativo['score']}")
        with col4:
            st.markdown('**Risco:**')
            compare_status(3, ativo['nota_risco'], f"{ativo['nota_risco']}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Indicadores")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('**Margem Liquida:**')
            compare_status(ativo['margem_liquida'], 0.1, f"{ativo['margem_liquida'] * 100:.2f}%")
        with col2:
            st.markdown('**Liquidez Corrente:**')
            st.info(f"{ativo['liquidez_corrente']:.2f}" if ativo['liquidez_corrente'] else "N/A")
        with col3:
            st.markdown('**Divida/EBITDA:**')
            div = ativo['divida_ebitda'] or 0
            compare_status(2, div, f"{div:.2f}") if div > 0 else st.error(f"{div:.2f}")

        with col1:
            st.markdown('**ROE:**')
            compare_status(ativo['roe'], indice_base / 100, f"{ativo['roe'] * 100:.2f}%")
        with col2:
            st.markdown('**Receita:**')
            compare_status(ativo['receita'], indice_base / 100, f"{ativo['receita'] * 100:.2f}%")
        with col3:
            st.markdown('**Lucro:**')
            compare_status(ativo['lucro'], indice_base / 100, f"{ativo['lucro'] * 100:.2f}%")

        with col1:
            st.markdown('**Earning Yield:**')
            compare_status(ativo['earning_yield'], indice_base, f"{ativo['earning_yield']:.2f}%")
        with col2:
            st.markdown('**Free Float:**')
            compare_status(ativo['free_float'], 30, f"{ativo['free_float']:.2f}%")
        with col3:
            st.markdown('**P/L:**')
            st.info(f"{ativo['pl']:.2f}" if ativo['pl'] else "N/A")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Dividendos")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Yield Anual Atual", f"{ativo['dy_estimado']:.2f}%", delta=f"R$ {ativo['dy_estimado'] * ativo['cotacao']:.2f}")
        with col2:
            atual = ativo['dy_estimado']
            estimado = ativo['dy_estimado']
            st.metric("Dividendos Anual Estimado", f"{estimado:.2f}%", delta=f"R$ {estimado * ativo['cotacao']:.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Guia de Compras")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Lucro X Cotação:**')
            teto = ativo.get('teto_por_lucro')
            if teto is not None:
                compare_status(teto, ativo['cotacao'], f"R$ {teto:.2f}")
            else:
                st.warning("Empresa com menos de 5 anos de B3")
        with col2:
            st.markdown('**Teto baseado em Dividendo Estimado**')
            compare_status(ativo['valor_teto_por_dy'], ativo['cotacao'], f"R$ {ativo['valor_teto_por_dy']:.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)
        st.subheader("Necessário para R$1000 mensais")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Cotas Necessárias:**')
            st.info("{:,.0f}".format(ativo['cotas_necessarias_para_1000_mensais']))
        with col2:
            st.markdown('**Investimento Necessário:**')
            st.info(f"R$ {ativo['investimento_necessario_para_1000_mensais']:,.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o ticker: {str(e)}")
