import yfinance as yf
import modules.investidor10 as investidor10
from datetime import datetime
import numpy as np


#criar objeto FII que ler o ticker
class FII:
    def __init__(self, ticker):
        self.ticker = ticker
        self.fii = yf.Ticker(ticker)

    @property
    def info(self):
        return self.fii.info

    @property
    def valor_patrimonial(self):
        # checa se Total Equity Gross Minority Interest existe
        if 'Total Equity Gross Minority Interest' not in self.fii.balance_sheet.index:
            return None
        return self.fii.balance_sheet.loc['Total Equity Gross Minority Interest'].head(1).values[0]

    @property
    def cotas_emitidas(self):
        if 'Ordinary Shares Number' not in self.fii.balance_sheet.index:
            return None
        if np.isnan(self.fii.balance_sheet.loc['Ordinary Shares Number'].head(1).values[0]):
            return None
        return self.fii.balance_sheet.loc['Ordinary Shares Number'].head(1).values[0]


    @property
    def vpa(self):
        if self.valor_patrimonial is None or self.cotas_emitidas is None:

            i10 = get_investidor10(self.ticker)
            return round(self.cotacao/i10.pvp,2)
        return round(self.valor_patrimonial / self.cotas_emitidas,2)

    @property
    def cotacao(self):
        # checa se existe a chave currentPrice no dicionário
        if 'currentPrice' in self.info:
            return self.info['currentPrice']
        return self.info['ask']


    @property
    def pvp(self):
        return round(self.cotacao / self.vpa,2)

    @property
    def dividends(self):
        return self.fii.dividends

    @property
    def dividend_yield(self):
        return self.dividends.tail(12).sum() / self.cotacao

    @property
    def historico_dividendos(self):
        return {
            '1 mes': self.dividends.tail(1).sum(),
            '3 meses': self.dividends.tail(3).sum(),
            '6 meses': self.dividends.tail(6).sum(),
            '12 meses': self.dividends.tail(12).sum(),
        }

    @property
    def dividendo_estimado(self):
        tres_meses = self.dividends.tail(3).sum()/3
        seis_meses = self.dividends.tail(6).sum()/6

        if tres_meses < seis_meses:
            return tres_meses *12
        return seis_meses*12

    @property
    def risco_liquidez(self):
        if "averageVolume" not in self.info:
            return 10
        volume = self.info.get("averageVolume", 0)
        if volume > 50000:
            return 1
        elif volume > 20000:
            return 5
        return 10

    @property
    def risco_tamanho(self):
        if "marketCap" not in self.info:
            return 10
        market_cap = self.info.get("marketCap", 0)
        if market_cap < 500_000_000:
            return 5
        return 1

    @property
    def risco_preco_volatilidade(self):
        if "52WeekChange" not in self.info:
            return 10
        variacao_52w = self.info.get("52WeekChange", 0)
        if variacao_52w < -0.15:
            return 10
        if variacao_52w < -0.05:
            return 5
        return 1

    @property
    def risco_rendimento(self):
        if "dividendYield" not in self.info:
            return 10
        dy = self.info.get("dividendYield", 0)
        if dy > 12:
            return 10
        if dy > 8:
            return 5
        if dy < 7:
            return 5
        return 1

    def overall_risk(self, risco_operacional):
        pesos = {
            "liquidez": 0.2,
            "tamanho_fundo": 0.1,
            "preco_volatilidade": 0.1,
            "rendimento": 0.3,
            "operacional": 0.3,
        }

        overall_risk = (
            (self.risco_liquidez * pesos["liquidez"]) +
            (self.risco_preco_volatilidade * pesos["preco_volatilidade"]) +
            (self.risco_tamanho * pesos["tamanho_fundo"]) +
            (self.risco_rendimento * pesos["rendimento"]) +
            (risco_operacional * pesos["operacional"])
        )

        # Normalizar para escala de 1 a 10
        return round(min(max(overall_risk, 1), 10),1)



def convert_unix_date(unix_date):
    date_time = datetime.fromtimestamp(unix_date)
    return date_time.strftime('%d/%m')


def get_investidor10(ticker):
    ticker= ticker.split(".")[0]
    return investidor10.FII(ticker)

def main():
    fii = FII('HSML11.SA')

    print(f"Ticker: {fii.ticker}")
    print(f"Valor Patrimonial: {fii.valor_patrimonial}")
    print(f"Cotas Emitidas: {fii.cotas_emitidas}")
    print(f"VPA: {fii.vpa}")
    print(f"Cotacao: {fii.cotacao}")
    print(f"PVP: {fii.pvp}")

    print(f"Dividend Yield: {fii.dividend_yield}")

    print(f"Dividendo estimado: {fii.dividendo_estimado}")

   # print(f"Histórico de dividendos: {fii.historico_dividendos}")
    print(f"Dividendos: {fii.dividends}")
    print(f"Risco de Liquidez: {fii.risco_liquidez}")
    print(f"Risco de Tamanho: {fii.risco_tamanho}")
    print(f"Risco de Preço e Volatilidade: {fii.risco_preco_volatilidade}")
    print(f"Risco de Rendimento: {fii.risco_rendimento}")
    print(f"over all risk: {fii.overall_risk(3)}")


    # pprint.pprint(fii.info)

if __name__ == '__main__':
    main()
