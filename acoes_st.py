import acoes
import score
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
        ativo = acoes.acao(f"{ticker}.SA")  # Inicializar objeto FII

        # # Verificar se o objeto fi possui os atributos necessários
        # if not all(hasattr(fi, attr) for attr in ['cotacao', 'dividend_yield', 'vpa', 'cotas_emitidas', 'pvp', 'valor_patrimonial', 'info']):
        #     st.error("Erro ao obter informações do FII. Verifique se o ticker está correto.")
        #     return

        # Configurações da página
        st.title(f"{ativo.acao.info.get('symbol', '')}")
        st.subheader(f"{ativo.acao.info.get('longName','')}")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Informações gerais
        st.subheader("Informações Gerais")
        col1, col2,col3,col4 = st.columns(4)

        with col1:
            st.markdown('**Cotação:**')
            st.info(f"R$ {ativo.cotacao}")
        with col2:
            st.markdown('**DY (12M):**')
            compare_status(ativo.dy, indice_base/100, f"{ativo.dy * 100:.2f}%")
        with col3:
            st.markdown('**Nota:**')
            nota = score.evaluate_company(ativo.acao,indice_base)
            compare_status(nota, 5, f"{nota}")
        with col4:
            #risco
            st.markdown('**Risco:**')
            risco = ativo.risco_geral
            compare_status(3, risco, f"{risco}")

        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Informações sobre valor patrimonial
        st.subheader("Indicadores")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('**Margem Liquida:**')
            compare_status(ativo.margem_liquida, 0.1, f"{ativo.margem_liquida*100:.2f}%")
        with col2:
            st.markdown('**Liquidez Corrente:**')
            if ativo.liquidez_corrente != None:
                compare_status(ativo.liquidez_corrente, 1, f"{ativo.liquidez_corrente:.2f}")
            else:
                st.warning("N/A")
        with col3:
            st.markdown('**Divida/EBITDA:**')
            div_ebitda = ativo.div_ebitda if ativo.div_ebitda != None else 0
            if div_ebitda > 0:
                compare_status(2, div_ebitda, f"{div_ebitda:.2f}")
            else:
                st.error(f"{div_ebitda:.2f}")

        with col1:
            st.markdown('**ROE:**')
            roe = ativo.roe if ativo.roe != None else 0
            compare_status(roe, indice_base/100, f"{roe*100:.2f}%")
        with col2:
            #receita
            st.markdown('**Receita:**')
            compare_status(ativo.receita, indice_base/100, f"{ativo.receita*100:.2f}%")
        with col3:
            st.markdown('**Lucro:**')
            compare_status(ativo.lucro, indice_base/100, f"{ativo.lucro*100:.2f}%")


        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # # Distribuições nos últimos 12 meses
        st.subheader("Dividendos")
        # # Aqui você pode adicionar gráficos ou tabelas para mostrar distribuições
        col1, col2, = st.columns(2)

        with col1:
             st.metric(label="Yield Anual Atual",value=f" {(ativo.dy)*100:.2f}%", delta=f"R$ {(ativo.dy*ativo.cotacao):,.2f}")
        with col2:
            atual = ativo.dy
            estimado = ativo.dy_estimado
            color = "inverse" if atual > estimado else "normal"
            st.metric(label="Dividendos Anual Estimado",value=f" {(ativo.dy_estimado)*100:.2f}%", delta=f"R$ {ativo.dy_estimado*ativo.cotacao:,.2f}", delta_color=color)


        # Linha de separação com cor customizada
        st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # Guia de Compras: Preço Teto, Yield Projetado e Dividendos Esperados
        st.subheader("Guia de Compras: Lucro X Cotação, Yield Projetado")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**Lucro X Cotação:**')
            if ativo.teto_cotacao_lucro != None:
                compare_status(ativo.teto_cotacao_lucro, ativo.cotacao, f"R$ {ativo.teto_cotacao_lucro:,.2f}")
            else:
                st.warning("Empresa com menos de 5 anos de B3")
        with col2:
            st.markdown('**Teto baseado em Dividendo Estimado**')
            dy_estimado = (ativo.dy_estimado*ativo.cotacao)/(indice_base/100) if ativo.dy_estimado else 0
            compare_status(dy_estimado, ativo.cotacao, f"R$ { dy_estimado:.2f}")


        # with col1:
        #     st.markdown('**Dividendos Estimados proximos 12m:**')
        #     compare_status(ativo.acao.dividendo_estimado, ativo.acao.historico_dividendos['12 meses'], f"R$ {ativo.acao.dividendo_estimado:,.2f}")

        # with col2:
        #     st.markdown('**Dividendos Estimado por mes**')
        #     compare_status(ativo.acao.dividendo_estimado/12, ativo.acao.historico_dividendos['12 meses']/12, f"R$ {ativo.acao.dividendo_estimado/12:,.2f}")

        # st.markdown("<hr style='background-color: #c4c4c4; height: 2px;'>", unsafe_allow_html=True)

        # st.text("Preço Teto baseado em dividendos")
        # tijolo = indice_base + 3
        # papel = indice_base + 5
        # infra = indice_base + 8

        # col1, col2, col3 = st.columns(3)

        # with col1:
        #     st.markdown('**Tijolo**')
        #     compare_status(ativo.acao.dividendo_estimado/tijolo*100, ativo.acao.cotacao, f"R$ {ativo.acao.dividendo_estimado/tijolo*100:.2f}")
        # with col2:
        #     st.markdown('**Papel**')
        #     compare_status(ativo.acao.dividendo_estimado/papel*100, ativo.acao.cotacao, f"R$ {ativo.acao.dividendo_estimado/papel*100:.2f}")
        # with col3:
        #     st.markdown('**Infra ou Agro**')
        #     compare_status(ativo.acao.dividendo_estimado/infra*100, ativo.acao.cotacao, f"R$ {ativo.acao.dividendo_estimado/infra*100:.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o ticker: {str(e)}")

