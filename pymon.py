import sys
from PyQt5.QtWidgets import *
import Kiwoom
import datetime
import webreader
import time
import numpy as np
from pandas import Series, DataFrame

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10


class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()

    # noinspection PyMethodMayBeStatic
    def run(self):
        df = self.get_ohlcv('039490', '20220701')
        print(df)

    # noinspection PyMethodMayBeStatic
    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.set_input_value('종목코드', code)
        self.kiwoom.set_input_value('기준일자', start)
        self.kiwoom.set_input_value('수정주가구분', 1)
        self.kiwoom.comm_rq_data('opt10081_req', 'opt10081', 0, '0101')
        time.sleep(0.2)

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                       index=self.kiwoom.ohlcv['date'])

        return df

    # noinspection PyMethodMayBeStatic
    def calculate_estimated_dividend_to_treasury(self, code):
        estimated_dividend_yield = webreader.get_estimated_dividend_yield(code)
        current_3year_treasury = webreader.get_current_3year_treasury()
        estimated_dividend_to_treasury = float(estimated_dividend_yield) / float(current_3year_treasury)

        return estimated_dividend_to_treasury

    # noinspection PyMethodMayBeStatic
    def get_min_max_dividend_to_treasury(self, code):
        previous_dividend_yield = webreader.get_previous_dividend_yield(code)
        three_years_treasury = webreader.get_3year_treasury()

        now = datetime.datetime.now()
        cur_year = now.year
        previous_dividend_to_treasury = {}

        for year in range(cur_year-5, cur_year):
            if year in previous_dividend_yield.keys() and year in three_years_treasury.keys():
                ratio = float(previous_dividend_yield[year]) / float(three_years_treasury[year])
                previous_dividend_to_treasury[year] = ratio

        print(f'dividend: {previous_dividend_to_treasury}')
        min_ratio = min(previous_dividend_to_treasury.values())
        max_ratio = max(previous_dividend_to_treasury.values())

        return min_ratio, max_ratio

    def buy_check_by_dividend_algorithm(self, code):
        estimated_dividend_to_treasury = self.calculate_estimated_dividend_to_treasury(code)
        (min_ratio, max_ratio) = self.get_min_max_dividend_to_treasury(code)

        if estimated_dividend_to_treasury >= max_ratio:
            return 1, estimated_dividend_to_treasury
        else:
            return 0, estimated_dividend_to_treasury


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pymon = PyMon()
    print(pymon.buy_check_by_dividend_algorithm('058470'))
