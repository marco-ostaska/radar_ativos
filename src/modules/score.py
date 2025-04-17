# Definindo os dados da empresa
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
        if debt_to_ebitda < 2:
            return 2
        if debt_to_ebitda < 3:
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

def score_risco_geral(data):
    if 'overallRisk' not in data.info:
        return -2

    if data.info['overallRisk'] >5:
        return -3

    if data.info['overallRisk'] == 1:
        return 2

    return 0

def score_free_float(data):
    if 'floatShares' not in data.info or 'sharesOutstanding' not in data.info:
        return 0
    if data.info['floatShares'] / data.info['sharesOutstanding'] *100 > 30:
        return 2
    return 0

def score_earning_yield(data, indice_base):
    if 'trailingPE' not in data.info:
        return 0
    earning_yield = (1 / data.info['trailingPE'])*100
    if earning_yield > indice_base:
        return 2    
    return -2




def calculate_max_score():
    max_score_trailingPE = 2  # Pontuação máxima para trailingPE
    max_score_priceToBook = 2  # Pontuação máxima para priceToBook
    max_score_priceToSales = 2  # Pontuação máxima para priceToSales
    max_score_grossMargins = 2  # Pontuação máxima para grossMargins
    max_score_operatingMargins = 2  # Pontuação máxima para operatingMargins
    max_score_profitMargins = 2  # Pontuação máxima para profitMargins
    max_score_earningsGrowth = 2  # Pontuação máxima para earningsGrowth
    max_score_debt_to_ebitda = 2  # Pontuação máxima para debt_to_ebitda
    max_score_revenueGrowth = 2  # Pontuação máxima para revenueGrowth
    max_score_currentRatio = 2  # Pontuação máxima para currentRatio
    max_score_quickRatio = 2  # Pontuação máxima para quickRatio
    max_score_dividendYield = 2  # Pontuação máxima para dividendYield
    max_score_payOutRatio = 2  # Pontuação máxima para payOutRatio
    max_score_beta = 2  # Pontuação máxima para beta
    max_score_risco_geral = 2  # Pontuação máxima para risco_geral
    max_score_free_float = 2  # Pontuação máxima para free_float
    max_score_earning_yield = 2  # Pontuação máxima para earning_yield

    max_score =  (
        max_score_trailingPE
        + max_score_priceToBook
        + max_score_priceToSales
        + max_score_grossMargins
        + max_score_operatingMargins
        + max_score_profitMargins
        + max_score_earningsGrowth
        + max_score_debt_to_ebitda
        + max_score_revenueGrowth
        + max_score_currentRatio
        + max_score_quickRatio
        + max_score_dividendYield
        + max_score_payOutRatio
        + max_score_beta
        + max_score_risco_geral
        + max_score_free_float
        + max_score_earning_yield
    )
    return max_score




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
    score += score_risco_geral(data)

    # Normalizando a pontuação para 0 a 10
    max_score = calculate_max_score()  # Máximo possível
    normalized_score = (score / max_score) * 10

    return round(normalized_score, 1)



def processar(data):
    # # Avaliando a empresa
    company_score = evaluate_company(data)
    return f"{company_score:.1f}"


def main():

    ativo = "CAML3.SA"
    data = yf.Ticker(ativo)

    print(evaluate_company(data))


if __name__ == '__main__':
    main()
