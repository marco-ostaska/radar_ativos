import yfinance as yf
import pprint


ativo = yf.Ticker("HSML11.SA")

pprint.pprint(ativo.info)


#'dividendRate': 7.52,
# 'dividendYield': 0.1342,
# liquidez corrent  'currentRatio': 1.079,
# profitMargins margem liquida
# payoutRatio = payout
# crescimento do receitas revenueGrowth
# crescimento de lucros profitGrowth ou earningsGrowth
# divida liquida (DÍVIDA LÍQUIDA / EBITDA) conta= div_liq = (totalDebt - totalCash) / ebitda
# Return on Equity (ROE) = returnOnEquity
