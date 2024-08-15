# Definindo os dados da empresa
import re
import yfinance as yf


def score_trailingPE(data):
    # checa se existe a chave trailingPE no dicionário

    if 'trailingPE' in data.info:
        if data.info['trailingPE'] < 10:
            return 2
        if data.info['trailingPE'] < 20:
            return 1
    return 0

def score_priceToBook(data):
    #checha se existe a chave priceToBook no dicionário
    if 'priceToBook' in data.info:
        if data.info['priceToBook'] < 1.5:
            return 2
        if data.info['priceToBook'] < 2:
            return 1
    return 0

def score_priceToSales(data):
    #checha se existe a chave priceToSalesTrailing12Months no dicionário
    if 'priceToSalesTrailing12Months' in data.info:
        if data.info['priceToSalesTrailing12Months'] < 2:
            return 2
        if data.info['priceToSalesTrailing12Months'] < 3:
            return 1
    return 0


def score_grossMargins(data):
    # checa se existe a chave grossMargins no dicionário
    if 'grossMargins' in data.info:
        if data.info['grossMargins'] > 0.40:
            return 2
        if data.info['grossMargins'] > 0.30:
            return 1
    return 0

def score_operatingMargins(data):
    # checa se existe a chave operatingMargins no dicionário
    if 'operatingMargins' in data.info:
        if data.info['operatingMargins'] > 0.30:
            return 2
        if data.info['operatingMargins'] > 0.20:
            return 1
    return 0

def score_profitMargins(data):
    # checa se existe a chave profitMargins no dicionário
    if 'profitMargins' in data.info:
        if data.info['profitMargins'] > 0.20:
            return 2
        if data.info['profitMargins'] > 0.10:
            return 1
    return 0

def score_earningsGrowth(data):
    # checa se existe a chave earningsGrowth no dicionário
    if 'earningsGrowth' in data.info:
        if data.info['earningsGrowth'] > 0.20:
            return 2
        if data.info['earningsGrowth'] > 0.10:
            return 1
    return 0

def score_debt_to_ebitda(data):
    # checa se existe a chave totalDebt e EBITDA no dicionário
    if 'totalDebt' in data.info and 'ebitda' in data.info:
        debt_to_ebitda = data.info['totalDebt'] / data.info['ebitda']
        if debt_to_ebitda < 3:
            return 2
        if debt_to_ebitda < 5:
            return 1
    return 0

def score_revenueGrowth(data):
    # checa se existe a chave revenueGrowth no dicionário
    if 'revenueGrowth' in data.info:
        if data.info['revenueGrowth'] > 0.10:
            return 2
        if data.info['revenueGrowth'] > 0.05:
            return 1
    return 0

def score_currentRatio(data):
    # checa se existe a chave currentRatio no dicionário
    if 'currentRatio' in data.info:
        if data.info['currentRatio'] > 1.5:
            return 2
        if data.info['currentRatio'] > 1.0:
            return 1
    return 0

def score_quickRatio(data):
    # checa se existe a chave quickRatio no dicionário
    if 'quickRatio' in data.info:
        if data.info['quickRatio'] > 1:
            return 2
        if data.info['quickRatio'] > 0.5:
            return 1
    return 0

def score_dividendYield(data, indice_base):
    # checa se existe a chave dividendYield no dicionário
    if 'dividendYield' in data.info:
        if data.info['dividendYield'] > indice_base:
            return 2
        if data.info['dividendYield'] == indice_base:
            return 1
    return 0

def score_payOutRatio(data):
    # checa se existe a chave payoutRatio no dicionário
    if 'payoutRatio' in data.info:
        if data.info['payoutRatio'] < 0.50:
            return 2
    return 0

def score_beta(data):
    # checa se existe a chave beta no dicionário
    if 'beta' in data.info:
        if data.info['beta'] < 1:
            return 2
    return 0

def evaluate_company(data, indice_base=7):
    score = 0
    score += score_trailingPE(data)
    score += score_priceToBook(data)
    score += score_priceToSales(data)
    score += score_grossMargins(data)
    score += score_operatingMargins(data)
    score += score_profitMargins(data)
    score += score_earningsGrowth(data)
    score += score_debt_to_ebitda(data)
    score += score_revenueGrowth(data)
    score += score_currentRatio(data)
    score += score_quickRatio(data)
    score += score_dividendYield(data, indice_base)
    score += score_payOutRatio(data)
    score += score_beta(data)

    # Normalizando a pontuação para 0 a 10
    max_score = 28  # Máximo possível
    normalized_score = (score / max_score) * 10

    return round(normalized_score, 1)



def processar(data):
    # # Avaliando a empresa
    company_score = evaluate_company(data)
    return f"{company_score:.1f}"

ativos = [
    "CSMG3",
    "CMIG4",
    "GGBR4",
    "BBAS3",
    "SAPR3",
    "KEPL3",
    "CPFE3",
    "PSSA3",
    "PETR3",
    "NEOE3",
    "BBSE3",
    "SLCE3",
    "FLRY3",
    "CAML3",
    "CXSE3",
    "POSI3",
    "EGIE3",
    "TOTS3",
    "VALE3",
    "ITUB3",
    "PRIO3",
    "RENT3",
    "RANI3",
    "AGRO3",
    "BBDC4",
    "EKTR3",
    "VIVA3",
    "ALOS3",
    "JALL3",
    "MGLU3",
    "GOAU3",
    "EQTL3"
]

for a in ativos:
    try:
        data = yf.Ticker(f"{a}.SA")
        nota = processar(data)
        margemLiquida = data.info['profitMargins']
        liquidezCorrente = data.info['currentRatio']
        div_ebitda = data.info['totalDebt'] / data.info['ebitda']
        dy = data.info['dividendYield']
        roe = data.info['returnOnEquity']
        profit = data.info['profitMargins']
        cotacao = data.info['currentPrice']
        dy_estimado = data.info['dividendRate'] / data.info['currentPrice']
        print(f"{a} - Nota: {nota} - Margem Líquida: {margemLiquida} - Liquidez Corrente: {liquidezCorrente} - Dívida/EBITDA: {div_ebitda} - DY: {dy} - ROE: {roe} - Lucro: {profit} - Cotacao: {cotacao} - Dividendo Estimado: {dy_estimado}")
    except Exception as e:
        print(f"Erro ao processar {a}: {str(e)}")
