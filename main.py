import os
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
from ativosYAML import montar_add, montar_remove

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .main {
        max-width: 70%; /* Ajuste o valor aqui para controlar a largura */
        margin: 0 auto; /* Centraliza o conteúdo */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def refresh_indices():
    now = f"{datetime.datetime.now():%d-%m-%Y}"
    try:
        selic = bc.SELIC(5)
        ipca = bc.IPCA(5)
        ipc_a =bc.IPCA(1)
        data = {
            'date': now,
            'selic': selic.media_ganho_real,
            'selic_atual': selic.atual,
            'ipca': ipca.media_ganho_real,
            'ipca_media5': ipca.media_anual,
            'ipca_atual': ipc_a.media_anual
        }

        with open('bc.json', 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(e)
        data = {
            'date': now,
            'selic': 0,
            'ipca': 0,
            'selic_atual': 0,
            'ipca_media5': 0,
            'ipca_atual': 0
        }
    # checa se bc.json existe

    if not os.path.exists('bc.json'):
        with open('bc.json', 'w') as file:
            json.dump(data, file)


def get_indices(force=False):
    # checa se arquivo bc.json existe
    try:
        with open('bc.json') as file:
            data = json.load(file)
            if data['date'].split('-')[1] == f"{datetime.datetime.now():%m}" and not force:
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

    col1, col2, col3, col4, col5,col6, col7, col8 = st.columns(8)

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
        #st.markdown('**Yield:**', help="Earning Yield para acoes e DY estimado para FII")
        st.markdown('**Yield:**')
    with col6:
        st.markdown('**Rendimento Real:**', help="Rendimento real do ativo baseado no indice de referencia")
    with col7:
        st.markdown('**Potencial:**')
    with col8:
        st.markdown('**Nota Atual:**', help="Nota de 0 a 10, baseada em critérios de análise fundamentalista")



def fmt_radar_fii(tipo, data, indice_base, indices):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        fi = fii.FII(f"{ticker['ticker']}.SA")

        spread = data[tipo]["spread"] + indice_base
        dy_estimado = (fi.dividendo_estimado*100)/fi.cotacao
        teto_div = fi.dividendo_estimado/spread*100


        col1, col2, col3, col4, col5,col6, col7, col8 = st.columns(8)

        with col1:
            st.info(fi.ticker.split(".")[0])
        with col2:
            st.info(f"R$ {fi.cotacao}")
        with col3:
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col4:
            compare_status(teto_div,fi.cotacao,  f"R$ {fi.dividendo_estimado/spread*100:.2f}")
        with col5:
            compare_status(dy_estimado, spread, f"{dy_estimado:.2f}%")
        with col6:
            rf_real = (indices['selic_atual'] - (indices['selic_atual'] * 0.15)) - indices['ipca_atual']
            maior = max(indices['ipca_atual'], rf_real)
            real = dy_estimado - indices['ipca_atual']
            compare_status(real, maior, f"{real:.2f}%")
        with col7:
            pot = round(((teto_div-fi.cotacao)/fi.cotacao)*100,2)
            compare_status(pot, 0, f"{pot}%")
        with col8:
            nota = scoreFII.evaluate_fii(fi, indice_base)
            compare_status(nota, 6, f"{nota}")


def fmt_radar_acoes(tipo, data, indice_base, indices):
    fmt_radar_head(tipo)

    for ticker in data[tipo]["tickers"]:
        ativo = acoes.acao(f"{ticker['ticker']}.SA")


        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

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
            #earning_yield = ativo.earning_yield
            dy_estimado = (ativo.dy_estimado)*100 if ativo.dy_estimado else 0
            compare_status(dy_estimado, indice_base, f"{dy_estimado:.2f}%")
        with col6:
            # earning_yield = ativo.earning_yield
            rf_real = (indices['selic_atual'] - (indices['selic_atual'] * 0.15)) - indices['ipca_atual']
            maior = max(indices['ipca_atual'], rf_real)
            dy_estimado = (ativo.dy_estimado)*100 if ativo.dy_estimado else 0
            real = dy_estimado - indices['ipca_atual']
            compare_status(real, maior, f"{real:.2f}%")

        with col7:
            dy_estimado = (ativo.dy_estimado*ativo.cotacao)/(indice_base/100) if ativo.dy_estimado else 0
            base = ativo.teto_cotacao_lucro if ativo.teto_cotacao_lucro else dy_estimado
            potencial = round((((base-ativo.cotacao)/ativo.cotacao)*100),2)
            compare_status(potencial,0, f"{potencial}%")
        with col8:
            nota = score.evaluate_company(ativo.acao, indice_base)
            compare_status(nota, 5, f"{nota}")

def fmt_radar_indice(indices):

    # SELIC
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('**Indice**')
    with col2:
        st.markdown('**Atual**')
    with col3:
            st.markdown('**Média 5 Anos**')
    with col4:
        st.markdown('**Juros Real**')



    col1, col2, col3, col4= st.columns(4)

    with col1:
        st.info("SELIC")
    with col2:
        st.info(f"{indices['selic_atual']}%")
    with col3:
        st.info(f"{indices['selic']}%")
    with col4:
        real= (indices['selic_atual'] - (indices['selic_atual'] * 0.15 )) - indices['ipca_atual']
        st.info(f"{round(real,2)}%")


    # IPCA

    col1, col2, col3, col4= st.columns(4)

    with col1:
        st.info("IPCA")
    with col2:
        st.info(f"{indices['ipca_atual']}%")
    with col3:
        st.info(f"{indices['ipca_media5']}%")
    with col4:
        st.info("N/A")


def radar(indice_base):

    indices = get_indices()
    # Botão para forçar o refresh
    if st.button("Atualizar Indices"):
        with st.spinner("Atualizando dados..."):
            indices = get_indices(force=True)
        st.success("Dados atualizados com sucesso!")
    fmt_radar_indice(indices)

    # adicionar o selecionador para acoes ou fii
    sl = st.selectbox("Selecione o tipo de ativo", ["", "FII", "Ações"])

    with open('ativos.yml', 'r') as file:
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

    cfg = st.sidebar.selectbox("Selecione a opção", ["", "Adicionar Ativos", "Remover Ativos"], index=0)
    if cfg == "Adicionar Ativos":
        montar_add()
    elif cfg == "Remover Ativos":
        montar_remove()




if __name__ == "__main__":
    main()
