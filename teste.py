import yfinance as yf
import fii
import yaml


with open('fii.yml', 'r') as file:
    data = yaml.safe_load(file)

print("Fiagro")
for ticker in data["fiagro"]["tickers"]:
    fi = fii.FII(f"{ticker['ticker']}.SA")
    print("Ticker: ", fi.ticker)
    print("Cotação: ", fi.cotacao)
    print("VPA: ", fi.vpa)
    spread = data["fiagro"]["spread"]
    # print()
    print("Teto DY: ", fi.dividendo_estimado/spread*100)


