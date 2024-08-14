import fii
import streamlit as st
import bancoCentral as bc
import fii_st
import yaml

@st.cache_data(ttl=86400)  # Cache por 24 horas (86400 segundos)
def melhor_indice():
    try: # Tenta obter o melhor índice
        selic = bc.SELIC(5)
        ipca = bc.IPCA(5)
        if selic.media_ganho_real > ipca.media_ganho_real:
            return selic.media_ganho_real
        return ipca.media_ganho_real
    except Exception as e:
        st.error(f"Erro ao obter o índices do Banco Central: usando valor default de 7 {str(e)}")
        return 7
# Faz cache do indice_base
indice_base = melhor_indice()

def compare_status(compare1, compare2, text):
    if compare1 == None or compare2 == None:
        return
    if compare1 > compare2:
        st.success(f"{text}")
    elif compare1 == compare2:
        st.warning(f"{text}")
    else:
        st.error(f"{text}")

def fmt_radar(tipo, data):

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('**Ativo:**')
    with col2:
        st.markdown('**Cotação:**')
    with col3:
        st.markdown('**Valor Patrimonial:**')
    with col4:
        st.markdown('**Valor Teto por DY:**')

    for ticker in data[tipo]["tickers"]:
        fi = fii.FII(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info(fi.ticker)
        with col2:
            st.info(f"R$ {fi.cotacao}")
        with col3:
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col4:
            spread = data[tipo]["spread"] + indice_base
            compare_status(fi.dividendo_estimado/spread*100, fi.cotacao, f"R$ {fi.dividendo_estimado/spread*100:.2f}")


def radar():

    with open('fii.yml', 'r') as file:
        data = yaml.safe_load(file)

    st.title("Radar de Ativos")
    st.subheader("TIJOLO")
    fmt_radar("tijolo", data)

    st.markdown("---")

    st.subheader("PAPEL")
    fmt_radar("papel", data)

    # add a separator
    st.markdown("---")

    st.subheader("FIAGRO")
    fmt_radar("fiagro", data)


# Caixa de texto para escolher o ativo
st.sidebar.title("Consulta de Ativos")
chk_radio = st.sidebar.radio("Selecione o tipo de ativo", ["FII", "Ações"], index=0)
ticker = st.sidebar.text_input('Digite o ticker do FII', help="Exemplo: HGLG11")

if ticker:
    if chk_radio == "FII":
        fii_st.processar(ticker, indice_base)
else:
    st.sidebar.warning("Por favor, insira o ticker de um FII para obter as informações.")
    radar()


