import fii
import scoreFII
import streamlit as st


def compare_status(compare1, compare2, text):
    if compare1 == None or compare2 == None:
        return
    if compare1 > compare2:
        st.success(f"{text}")
    elif compare1 == compare2:
        st.warning(f"{text}")
    else:
        st.error(f"{text}")

def format_millions_billions(value):
    if value == None:
        return
    if value >= 1e9:
        formatted = "{:.2f}b".format(value / 1e9)
    elif value >= 1e6:
        formatted = "{:.2f}M".format(value / 1e6)
    else:
        formatted = "{:.2f}".format(value)
    return formatted


# Função para processar o ticker e exibir informações
def processar(ticker, indice_base):
    try:
        fi = fii.FII(f"{ticker}.SA")  # Inicializar objeto FII

        # Verificar se o objeto fi possui os atributos necessários
        if not all(hasattr(fi, attr) for attr in ['cotacao', 'dividend_yield', 'vpa', 'cotas_emitidas', 'pvp', 'valor_patrimonial', 'info']):
            st.error("Erro ao obter informações do FII. Verifique se o ticker está correto.")
            return

        # Configurações da página
        st.title(f"{fi.info.get('symbol', '')}")
        st.subheader(f"{fi.info.get('longName','')}")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Informações gerais
        st.subheader("Informações Gerais")
        col1, col2,col3 = st.columns(3)

        with col1:
            st.markdown('**Cotação:**')
            st.info(f"R$ {fi.cotacao}")
        with col2:
            st.markdown('**DY (12M):**')
            st.info(f"{fi.dividend_yield * 100:.2f}%")
        with col3:
            st.markdown('**Nota:**')
            nota = scoreFII.evaluate_fii(fi,indice_base)
            compare_status(nota, 6, f"{nota}/10")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Informações sobre valor patrimonial
        st.subheader("Informações sobre Valor Patrimonial")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**Valor Patrimonial Por Cota:**', help="Pode ser usado como Teto de Preço baseado em valor patrimonial")
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col2:
            st.markdown('**Número De Cotas:**')
            st.info(f"{format_millions_billions(fi.cotas_emitidas)}")

        with col1:
            st.markdown('**P/VP:**',  help="Valores proximo a 1 indica que o FII está sendo negociado próximo ao seu valor patrimonial")
            compare_status(1, fi.pvp, f"{fi.pvp}")
        with col2:
            st.markdown('**Valor Patrimonial:**')
            st.info(f"R$ {format_millions_billions(fi.valor_patrimonial)}")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Distribuições nos últimos 12 meses
        st.subheader("Distribuições nos Últimos 12 Meses")
        # Aqui você pode adicionar gráficos ou tabelas para mostrar distribuições
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="Yield 1 Mês",value=f" {(fi.historico_dividendos['1 mes'] / fi.cotacao)*100:.2f}%", delta=f"R$ {fi.historico_dividendos['1 mes']:,.2f}")
        with col2:
            st.metric(label="Yield 3 meses",value=f" {(fi.historico_dividendos['3 meses'] / fi.cotacao)*100:.2f}%", delta=f"R$ {fi.historico_dividendos['3 meses']:,.2f}")
        with col3:
            st.metric(label="Yield 6 meses",value=f" {(fi.historico_dividendos['6 meses'] / fi.cotacao)*100:.2f}%", delta=f"R$ {fi.historico_dividendos['6 meses']:,.2f}")
        with col4:
            st.metric(label="Yield 12 meses",value=f" {(fi.historico_dividendos['12 meses'] / fi.cotacao)*100:.2f}%", delta=f"R$ {fi.historico_dividendos['12 meses']:,.2f}")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Guia de Compras: Preço Teto, Yield Projetado e Dividendos Esperados
        st.subheader("Guia de Compras: Preço Teto, Yield Projetado")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**Valor Patrimonial Por Cota:**', help="Pode ser usado como Teto de Preço baseado em valor patrimonial")
            compare_status(fi.vpa, fi.cotacao, f"R$ {fi.vpa}")
        with col2:
            st.markdown('**Yield estimado proximos 12m**')
            compare_status(fi.dividendo_estimado/fi.cotacao*100, fi.dividend_yield*100, f"{fi.dividendo_estimado/fi.cotacao*100:.2f}%")


        with col1:
            st.markdown('**Dividendos Estimados proximos 12m:**')
            compare_status(fi.dividendo_estimado, fi.historico_dividendos['12 meses'], f"R$ {fi.dividendo_estimado:,.2f}")

        with col2:
            st.markdown('**Dividendos Estimado por mes**')
            compare_status(fi.dividendo_estimado/12, fi.historico_dividendos['12 meses']/12, f"R$ {fi.dividendo_estimado/12:,.2f}")

        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        st.text("Preço Teto baseado em dividendos")
        tijolo = indice_base + 3
        papel = indice_base + 5
        infra = indice_base + 8

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('**Tijolo**')
            compare_status(fi.dividendo_estimado/tijolo*100, fi.cotacao, f"R$ {fi.dividendo_estimado/tijolo*100:.2f}")
        with col2:
            st.markdown('**Papel**')
            compare_status(fi.dividendo_estimado/papel*100, fi.cotacao, f"R$ {fi.dividendo_estimado/papel*100:.2f}")
        with col3:
            st.markdown('**Infra ou Agro**')
            compare_status(fi.dividendo_estimado/infra*100, fi.cotacao, f"R$ {fi.dividendo_estimado/infra*100:.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o ticker: {str(e)}")

