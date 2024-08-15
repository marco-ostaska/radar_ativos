from re import S
import fii as fiiLib
import pprint



def score_dy(fii_data, indice_base):
    # Dividend Yield
    # 8 = excelente
    # 5 = otimo
    # 3 = bom
    # indice_base = regular
    # else = ruim

    if fii_data.dividend_yield > (indice_base + 3)/100:
        return 2

    if fii_data.dividend_yield ==  indice_base/100 :
        return 1

    return 0

def score_preco_medio(fii_data):
    if 'currentPrice' not in fii_data.info or 'fiftyDayAverage' not in fii_data.info or 'fiftyTwoWeekHigh' not in fii_data.info:
        return 0

    score = 0

    # Preço Atual vs. Preço Médio
    if fii_data.cotacao > fii_data.info['fiftyTwoWeekHigh'] * 0.90:
        score += 1  # Bom, mas não ótimo

    if fii_data.cotacao < fii_data.info['fiftyDayAverage']:
        score += 1  # Bom, indica possível oportunidade de compra

    return max(score, 0)

def score_market_cap(fii_data):
    if 'marketCap' not in fii_data.info:
        return 0

    if fii_data.info['marketCap'] > 1e9:
        return 2  # Muito bom

    if fii_data.info['marketCap'] > 5e8:
        return 1  # Bom

    return 0  # Regular

def score_volume_medio(fii_data):
    if 'averageVolume' not in fii_data.info:
        return 0

    if fii_data.info['averageVolume'] > 50000:
        return 1  # Bom

    return 0  # Regular

def score_dividendos_crescentes(fii_data, indice_base):
    if fii_data.dividend_yield > (indice_base + 3)/100:
        return 2  # excelente
    if fii_data.dividend_yield > (indice_base + 1)/100:
        return 1  # bom
    return 0  # regular

def score_vpa(fii_data):
    if fii_data.vpa > fii_data.cotacao:
        return 1  # Muito bom
    if fii_data.vpa == fii_data.cotacao:
        return 0  # Bom
    return -2  # Regular

def bazin_score(fii_data, indice_base):
    if fii_data.cotacao < fii_data.dividendo_estimado/(indice_base+3)*100:
        return 1
    return -1


def calculate_max_score():
    max_dy_score = 2  # Pontuação máxima para Dividend Yield
    max_preco_medio_score = 2  # Pontuação máxima para Preço Médio
    max_market_cap_score = 2  # Pontuação máxima para Capitalização de Mercado
    max_volume_medio_score = 1  # Pontuação máxima para Volume Médio
    max_dividendos_crescentes_score = 2  # Pontuação máxima para Dividendos Crescentes
    max_vpa_score = 1  # Pontuação máxima para Valor Patrimonial por Ação
    max_bazin_score = 1  # Pontuação máxima para Bazin

    return (
        max_dy_score
        + max_preco_medio_score
        + max_market_cap_score
        + max_dividendos_crescentes_score
        + max_volume_medio_score
        + max_vpa_score
        + max_bazin_score
    )


def evaluate_fii(fii_data, indice_base):
    score = 0

    score += score_dy(fii_data, indice_base)
    score += score_preco_medio(fii_data)
    score += score_market_cap(fii_data)
    score += score_dividendos_crescentes(fii_data, indice_base)
    score += score_volume_medio(fii_data)
    score += score_vpa(fii_data)
    score += bazin_score(fii_data, indice_base)




    # Normalizando a pontuação para 0 a 10
    max_score = calculate_max_score()  # Máximo possível com base nos critérios
    normalized_score = (score / max_score) * 10

    return round(normalized_score, 1)



def main():
    # iniciar ativo
    fii_data = fiiLib.FII('HSLG11.SA')

    # Avaliando o FII
    fii_score = evaluate_fii(fii_data, 7)
    print(f"Nota do FII: {fii_score}/10")

if __name__ == "__main__":
    main()
