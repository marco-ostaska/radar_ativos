import pandas as pd
from datetime import datetime
import requests
import json

class Indices:
    def __init__(self, anos_hist):
        self.anos_hist = anos_hist
        self.df = None

    def get_url(self, codigo_serie):
        ontem = datetime.now() - pd.Timedelta(days=1)
        data_inicio = f"{ontem.day}/{ontem.month}/{ontem.year-self.anos_hist}"
        data_final = f"{ontem.day}/{ontem.month}/{ontem.year}"
        URL = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={data_inicio}&dataFinal={data_final}"
        print(URL)
        return URL

    def parse(self, codigo_serie, indice):
        if self.df is None:
            URL = self.get_url(codigo_serie)
            response = requests.get(URL)
            response.raise_for_status()
            data = json.loads(response.text)
            df = pd.DataFrame(data)
            df.rename(columns={"data": "date"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"], format='%d/%m/%Y')
            df.set_index('date', inplace=True)
            df["valor"] = df["valor"].str.replace(',', '.').astype(float)
            df.rename(columns={"valor": indice}, inplace=True)
            self.df = df
        return self.df

class SELIC(Indices):
    def __init__(self, anos_hist):
        super().__init__(anos_hist)
        self.codigo_serie = 11
        self.indice = "Selic"

    @property
    def media_anual(self):
        dias_uteis = 22
        media = self.parse(self.codigo_serie, self.indice).mean().dropna().values[0] * dias_uteis * 12
        return round(media, 2)

    @property
    def media_ganho_real(self):
        return  round(self.media_anual * (1 - 0.15),2)

    @property
    def atual(self):
        taxa_diaria = self.parse(self.codigo_serie, self.indice).iloc[-1].values[0] /100
        return round(((1 + taxa_diaria) ** 252 - 1) *100,2)



class IPCA(Indices):
    def __init__(self, anos_hist):
        super().__init__(anos_hist)
        self.codigo_serie = 10844
        self.indice = "IPCA"

    @property
    def media_anual(self):
        media = self.parse(self.codigo_serie, self.indice).mean().dropna().values[0] * 12
        return round(media, 2)

    @property
    def media_ganho_real(self):
        return self.media_anual + 2




def taxa_livre_risco(anos_hist):
    selic = SELIC(anos_hist)
    ipca = IPCA(anos_hist)

    if ipca.media_ganho_real() > selic.media_anual():
        return ipca.media_ganho_real()

    return selic.media_anual()



def main():
    selic = SELIC(1)
    ipca = IPCA(1)
    print(selic.atual, selic.media_anual, selic.media_ganho_real-ipca.media_anual , ipca.media_anual, ipca.media_ganho_real)



if __name__ == "__main__":
    main()
