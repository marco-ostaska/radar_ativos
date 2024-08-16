from calendar import c
import yfinance as yf
import pandas as pd
import fii
import yaml
from scipy.stats import trim_mean
from math import sqrt
import score


class acao:
    def __init__(self, ticker):
        self.ticker = ticker
        self.acao = yf.Ticker(ticker)
        self.adj_close = yf.download(ticker, period="5y", progress=False)["Adj Close"]

    def media_ponderada_fechamento(self, ano):
        return trim_mean(self.adj_close.loc[f"{ano}-"].tail(30).values, proportiontocut=0.1)

    @property
    def teto_cotacao_lucro(self):
        try:
            dates = list(self.acao.income_stmt.loc['Net Income'].dropna().tail(5).index.year)
            lucro = list(self.acao.income_stmt.loc['Net Income'].dropna().tail(5).values)
            cotacoes = [round(self.media_ponderada_fechamento(d), 2) for d in dates]
            # invertendo a ordem das listas
            dates = dates[::-1]
            lucro = lucro[::-1]
            cotacoes = cotacoes[::-1]

            # montar dict
            dados = {
                'Ano': dates,
                'Lucro Liquido': lucro,
                'Cotacao': cotacoes
            }

            #dataframe
            df = pd.DataFrame(dados)

            # Normalizar o valor do lucro liquido para escala de cotacao
            ultimo_lucro = df['Lucro Liquido'].iloc[-1]
            min_cotacao = df['Cotacao'].min()
            max_cotacao = df['Cotacao'].max()
            min_lucro = df['Lucro Liquido'].min()
            max_lucro = df['Lucro Liquido'].max()

            normalizado = round(min_cotacao + (ultimo_lucro - min_lucro) * (max_cotacao - min_cotacao) / (max_lucro - min_lucro),2)


            # verificar se o ultimo lucro liquido foi negativo
            if ultimo_lucro < 0 and self.acao.info['previousClose'] < 1:

                ajuste = round(sqrt(normalizado * self.acao.info['previousClose']) / (self.acao.info['previousClose']*100),2)
                return min(ajuste, normalizado)

            if ultimo_lucro < 0 and self.acao.info['previousClose'] > 1:
                ajuste = round(sqrt(normalizado * self.acao.info['previousClose']), 2)
                return min(ajuste, normalizado)


            # Calcular o valor normalizada do ultimo lucro na escala de cotaçao
            return normalizado
        except:
            return None



    @property
    def cotacao(self):
        return self.acao.info['previousClose'] if 'previousClose' in self.acao.info else self.acao.info['ask']

    @property
    def margem_liquida(self):
        return self.acao.info['profitMargins'] if 'profitMargins' in self.acao.info else None

    @property
    def liquidez_corrente(self):
        return self.acao.info['quickRatio'] if 'quickRatio' in self.acao.info else None

    @property
    def div_ebitda(self):
        return self.acao.info['div_ebitda'] if 'div_ebitda' in self.acao.info else None

    @property
    def dy(self):
        return self.acao.info['dividendYield'] if 'dividendYield' in self.acao.info else 0

    @property
    def roe(self):
        return self.acao.info['returnOnEquity'] if 'returnOnEquity' in self.acao.info else None

    @property
    def recomendacao(self):
        return self.acao.info['recommendationKey'] if 'recommendationKey' in self.acao.info else None

    # @property
    # def nota(self):
    #     return score.evaluate_company(self.acao)

    @property
    def lucro(self):
        return self.acao.info['profitMargins'] if 'profitMargins' in self.acao.info else None

    @property
    def dy_estimado(self):
        if 'dividendRate' in self.acao.info and 'currentPrice' in self.acao.info:
            return self.acao.info['dividendRate'] / self.acao.info['currentPrice']
        return None

    @property
    def risco_geral(self):
        return self.acao.info['overallRisk'] if 'overallRisk' in self.acao.info else None







def main():
    ativo = acao("POSI3.SA")
    print("Teto cotaçao x lucro:", ativo.teto_cotacao_lucro)
    print("Cotacao:", ativo.cotacao)
    print("Margem liquida:", ativo.margem_liquida)
    print("Liquidez corrente:", ativo.liquidez_corrente)
    print("Divida/EBITDA:", ativo.div_ebitda)
    print("DY:", ativo.dy)
    print("ROE:", ativo.roe)
    print("Recomendacao:", ativo.recomendacao)
    # print("Nota:", ativo.nota)
    print("Lucro:", ativo.lucro)
    print("DY estimado:", ativo.dy_estimado)
    print("Risco geral:", ativo.risco_geral)



if __name__ == "__main__":
    main()

