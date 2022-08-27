import requests
import re
import pandas as pd
import datetime
from bs4 import BeautifulSoup


def get_financial_statements(code):
    re_enc = re.compile("encparam: '(.*)'", re.IGNORECASE)
    re_id = re.compile("id: '([a-zA-Z\\d]*)' ?", re.IGNORECASE)

    url = f'http://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd={code}'
    html = requests.get(url).text
    encparam = re_enc.search(html).group(1)
    encid = re_id.search(html).group(1)

    url = (f'http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd={code}'
           f'&fin_typ=0&freq_typ=A&encparam={encparam}&id={encid}')
    headers = {'Referer': 'HACK'}
    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, 'html5lib')
    dividend = soup.select('table:nth-of-type(2) tr:nth-of-type(31) td span')
    years = soup.select('table:nth-of-type(2) tr:nth-of-type(2) th')

    dividend_dict = {}
    for i in range(len(dividend)):
        dividend_dict[years[i].text.strip()[:4]] = dividend[i].text

    return dividend_dict


def get_3year_treasury():
    url = 'http://www.index.go.kr/strata/jsp/showStblGams3.jsp?stts_cd=107301&amp;idx_cd=1073&amp;freq=Y'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html5lib')
    td_data = soup.select('tr td')

    treasury_3year = {}
    start_year = 1997

    for i in range(25):
        treasury_3year[start_year] = td_data[i].text
        start_year += 1

    return treasury_3year


def get_current_3year_treasury():
    url = 'http://finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page=1'
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html5lib')
    td_data = soup.select('tr td')
    return td_data[1].text


def get_dividend_yield(code):
    url = 'http://companyinfo.ock.naver.com/company/c1010001.aspx?cmp_cd=' + code
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'html5lib')
    dt_data = soup.select('tr td dl dt')

    dividend_yield = dt_data[-2].text
    dividend_yield = dividend_yield.split(' ')[1]
    dividend_yield = dividend_yield[:-1]

    print(dividend_yield)


def get_estimated_dividend_yield(code):
    dividend_yield = get_financial_statements(code)
    dividend_yield = sorted(dividend_yield.items())[-1]
    return dividend_yield[1]


def get_previous_dividend_yield(code):
    dividend_yield = get_financial_statements(code)

    now = datetime.datetime.now()
    cur_year = now.year

    previous_dividend_yield = {}

    for year in range(cur_year-5, cur_year):
        if str(year) in dividend_yield:
            previous_dividend_yield[year] = dividend_yield[str(year)]

    return previous_dividend_yield


if __name__ == '__main__':
    print(get_previous_dividend_yield('058470'))
