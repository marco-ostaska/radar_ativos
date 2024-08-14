import yfinance as yf
import investidor10
from datetime import datetime


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


def convert_unix_date(unix_date):
    date_time = datetime.fromtimestamp(unix_date)
    return date_time.strftime('%d/%m')


def get_investidor10(ticker):
    ticker= ticker.split(".")[0]
    return investidor10.FI_INFRA(ticker)

def main():
    fii = FII('MAXR11.SA')

    print(f"Ticker: {fii.ticker}")
    print(f"Valor Patrimonial: {fii.valor_patrimonial}")
    print(f"Cotas Emitidas: {fii.cotas_emitidas}")
    print(f"VPA: {fii.vpa}")
    print(f"Cotacao: {fii.cotacao}")
    print(f"PVP: {fii.pvp}")

    print(f"Dividend Yield: {fii.dividend_yield}")

    print(f"Dividendo estimado: {fii.dividendo_estimado}")

    print(f"Histórico de dividendos: {fii.historico_dividendos}")
    print(f"Dividendos: {fii.dividends}")


    # pprint.pprint(fii.info)

if __name__ == '__main__':
    main()
