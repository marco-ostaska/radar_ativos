import base64
import json
import datetime
import streamlit as st
import yaml
import acoes
import acoes_st
import bancoCentral as bc
import fii
import fii_st
import score
import scoreFII

def refresh_indices():
    now = f"{datetime.datetime.now():%d-%m-%Y}"
    try:
        selic = bc.SELIC(5)
        ipca = bc.IPCA(5)
        data = {
            'date': now,
            'selic': selic.media_ganho_real,
            'ipca': ipca.media_ganho_real
        }
    except Exception as e:
        data = {
            'date': now,
            'selic': 7,
            'ipca': 6.5
        }


    with open('bc.json', 'w') as file:
        json.dump(data, file)


def get_indices():
    # checa se arquivo bc.json existe
    try:
        with open('bc.json') as file:
            data = json.load(file)
            if data['date'].split('-')[1] == f"{datetime.datetime.now():%m}":
                return data
            refresh_indices()
            return get_indices()
    except FileNotFoundError:
        refresh_indices()
        return get_indices()

def melhor_indice():
    indices = get_indices()
    selic = indices['selic']
    ipca = indices['ipca']
    return max(selic, ipca)


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

    col1, col2, col3, col4, col5,col6 = st.columns(6)

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
        st.markdown('**Yield:**', help="Earning Yield para acoes e DY estimado para FII")
    with col6:
        st.markdown('**Nota Atual Para Comprar:**', help="Nota de 0 a 10, baseada em critérios de análise fundamentalista")



def fmt_radar_fii(tipo, data, indice_base):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        fi = fii.FII(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.info(fi.ticker.split(".")[0])
        with col2:
            st.info(f"R$ {fi.cotacao}")
        with col3:
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col4:
            spread = data[tipo]["spread"] + indice_base
            compare_status(fi.dividendo_estimado/spread*100, fi.cotacao, f"R$ {fi.dividendo_estimado/spread*100:.2f}")
        with col5:
            dy_estimado = (fi.dividendo_estimado*100)/fi.cotacao
            spread = data[tipo]["spread"] + indice_base
            compare_status(dy_estimado, spread, f"{dy_estimado:.2f}%")

        with col6:
            nota = scoreFII.evaluate_fii(fi, indice_base)
            compare_status(nota, 6, f"{nota}")


def fmt_radar_acoes(tipo, data, indice_base):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        ativo = acoes.acao(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.info(ativo.ticker.split(".")[0])
        with col2:
            st.info(f"R$ {ativo.cotacao}")
        with col3:
            compare_status(ativo.teto_cotacao_lucro, ativo.cotacao, f"R$ {ativo.teto_cotacao_lucro}")
        with col4:
            dy_estimado = (ativo.dy_estimado*ativo.cotacao)/(indice_base/100) if ativo.dy_estimado else 0
            compare_status(dy_estimado, ativo.cotacao, f"R$ { dy_estimado:.2f}")
        with col5:
            earning_yield = ativo.earning_yield
            compare_status(earning_yield, indice_base, f"{earning_yield:.2f}%")
        with col6:
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
    if ticker := st.sidebar.text_input('Digite o ticker do FII', help="Exemplo: HGLG11"):
        if chk_radio == "FII":
            fii_st.processar(ticker, indice_base)
        if chk_radio == "Ações":
            acoes_st.processar(ticker, indice_base)
    else:
        st.sidebar.warning("Por favor, insira o ticker de um FII para obter as informações.")
        radar(indice_base)


    # adicionar opt de upload para subistituir o ativos.yml
    st.sidebar.markdown("---")
    st.sidebar.title("Configurações")

    # adicionar ativos em FII
    st.sidebar.subheader("Adicionar ativos em FII")


    if st.sidebar.button("Download ativos.yml", help="Baixa o arquivo ativos.yml"):
        with open('ativos.yml', 'r') as file:
            data = file.read()
        b64 = base64.b64encode(data.encode()).decode()

        href = f'<a href="data:file/yml;base64,{b64}" download="ativos.yml">Download ativos.yml</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

    st.sidebar.markdown("---")


    if arquivo := st.sidebar.file_uploader("Upload ativos.yml", type="yml", help="Substitui o arquivo ativos.yml"):
        with open('ativos.yml', 'wb') as file:
            file.write(arquivo.getvalue())
        st.sidebar.success("Arquivo salvo com sucesso!")



if __name__ == "__main__":
    main()
