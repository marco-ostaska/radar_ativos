from calendar import c
import yfinance as yf
import pandas as pd
import fii
import yaml
from scipy.stats import trim_mean



def media_ponderada_fechamento(data, ano):

    return trim_mean(data.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)



ticker="PRIO3.SA"

data = yf.Ticker(ticker)


# lucro liquido
net_income = list(data.income_stmt.loc['Net Income'].dropna().tail(5).values)


dates = list(data.income_stmt.loc['Net Income'].dropna().tail(5).index.year)

dh = yf.download(ticker, period="5y", progress=False)["Adj Close"]


cotacoes = [round(media_ponderada_fechamento(dh,d),2) for d in dates]


# invertendo a ordem das listas
dates = dates[::-1]
net_income = net_income[::-1]
cotacoes = cotacoes[::-1]

# montar dict

dados = {
    'Ano': dates,
    'Lucro Liquido': net_income,
    'Cotacao': cotacoes
}


#| montando o dataframe
df = pd.DataFrame(dados)

# Normalizar o valor do lucro liquido para escala de cotacao

ultimo_lucro = df['Lucro Liquido'].iloc[-1]
min_cotacao = df['Cotacao'].min()
max_cotacao = df['Cotacao'].max()
min_lucro = df['Lucro Liquido'].min()
max_lucro = df['Lucro Liquido'].max()

# Calcular o valor normalizada do ultimo lucro na escala de cotaçao
valor_normalizado = min_cotacao + (ultimo_lucro - min_lucro) * (max_cotacao - min_cotacao) / (max_lucro - min_lucro)

print(dados)

print(valor_normalizado)



