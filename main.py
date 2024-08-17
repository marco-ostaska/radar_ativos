import fii
import streamlit as st
import bancoCentral as bc
import fii_st
import yaml
import scoreFII
import acoes
import acoes_st
import score

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


def compare_status(compare1, compare2, text):
    if compare1 == None or compare2 == None:
        return
    if compare1 > compare2:
        st.success(f"{text}")
    elif compare1 == compare2:
        st.warning(f"{text}")
    else:
        st.error(f"{text}")

def fmt_radar_head(tipo):

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('**Ativo:**')
    with col2:
        st.markdown('**Cotação:**')
    with col3:
        if tipo == "acoes":
            st.markdown('**cotação x lucro:**', help="Se vazio é pq empresa não possiu dados o suficiente, provavelmente é nova")
        else:
            st.markdown('**Valor Patrimonial:**')
    with col4:
        st.markdown('**Valor Teto por DY:**', help="Valor do DY estimado baseado no spread (média IPCA ou Selic, ultimos 5 anos, o que for maior) e no valor do ativo")
    with col5:
        st.markdown('**Nota Atual Para Comprar:**', help="Nota de 0 a 10, baseada em critérios de análise fundamentalista")

def fmt_radar_fii(tipo, data, indice_base):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        fi = fii.FII(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.info(fi.ticker)
        with col2:
            st.info(f"R$ {fi.cotacao}")
        with col3:
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col4:
            spread = data[tipo]["spread"] + indice_base
            compare_status(fi.dividendo_estimado/spread*100, fi.cotacao, f"R$ {fi.dividendo_estimado/spread*100:.2f}")
        with col5:
            nota = scoreFII.evaluate_fii(fi, indice_base)
            compare_status(nota, 6, f"{nota}")

def fmt_radar_acoes(tipo, data, indice_base):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        ativo = acoes.acao(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.info(ativo.ticker)
        with col2:
            st.info(f"R$ {ativo.cotacao}")
        with col3:
            compare_status(ativo.teto_cotacao_lucro, ativo.cotacao, f"R$ {ativo.teto_cotacao_lucro}")
        with col4:
            dy_estimado = (ativo.dy_estimado*ativo.cotacao)/(indice_base/100) if ativo.dy_estimado else 0
            compare_status(dy_estimado, ativo.cotacao, f"R$ { dy_estimado:.2f}")
        with col5:
            nota = score.evaluate_company(ativo.acao, indice_base)
            compare_status(nota, 5, f"{nota}")

def radar(indice_base):

    # adicionar o selecionador para acoes ou fii
    sl = st.selectbox("Selecione o tipo de ativo", ["", "FII", "Ações"])

    with open('ativos.yml', 'r') as file:
        data = yaml.safe_load(file)

    st.title("Radar de Ativos")

    if sl == "FII":
        for tipo in ["shopping", "logistica", "papel", "hibrido", "fiagro", "infra"]:
            st.subheader(tipo.upper())
            fmt_radar_fii(tipo, data, indice_base)

    if sl == "Ações":

        st.markdown("---")
        st.subheader("Ações")
        fmt_radar_acoes("acoes", data, indice_base)
        # fmt_radar("acoes", data)


def main():

    indice_base = melhor_indice()

    # Caixa de texto para escolher o ativo
    st.sidebar.title("Consulta de Ativos")
    chk_radio = st.sidebar.radio("Selecione o tipo de ativo", ["FII", "Ações"], index=0)
    ticker = st.sidebar.text_input('Digite o ticker do FII', help="Exemplo: HGLG11")

    if ticker:
        if chk_radio == "FII":
            fii_st.processar(ticker, indice_base)
        if chk_radio == "Ações":
            acoes_st.processar(ticker, indice_base)
    else:
        st.sidebar.warning("Por favor, insira o ticker de um FII para obter as informações.")
        radar(indice_base)


if __name__ == "__main__":
    main()
