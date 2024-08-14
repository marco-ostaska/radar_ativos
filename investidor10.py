import requests
from bs4 import BeautifulSoup

class Ativos:

    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
               'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
               'Accept-Encoding': 'gzip, deflate',
               }

    def __init__(self) -> None:
        self.soup = self.download_info()

    def download_info(self):
        url = f"http://investidor10.com.br/fiis/{self.ticker}"
        content = requests.get(url, headers=self.headers)
        return BeautifulSoup(content.content, 'html.parser', from_encoding='utf-8')


class FI_INFRA(Ativos):

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        super().__init__()

    @property
    def cotacao(self):

        cotacao_span = self.soup.find('span', class_='value')
        cotacao = cotacao_span.text.strip()
        return float(cotacao.replace("R$ ","").replace(",","."))


    @property
    def div_yield(self):
        tag = self.soup.find('span', title='Dividend Yield')
        value = tag.find_next('span').text.strip()
        return float(value.replace("%","").replace(",","."))


    @property
    def pvp(self):
        tag = self.soup.find('span', title='P/VP')
        value = tag.find_next('span').text.strip()
        return float(value.replace(",","."))




def fix_pct(text):
    return text.replace("%", "").replace(",", ".")


def main():



    acao = FI_INFRA("vgia11")
    print("Ticker :", acao.ticker)
    print("Cotacao:", acao.cotacao)
    print("PVP    :", acao.pvp)
    print("DY     :", acao.div_yield)


if __name__ == "__main__":
    main()


def main():
    pass

if __name__ == "__main__":
    main()
