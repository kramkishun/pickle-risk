from flask import Blueprint, current_app, request
from flask_pymongo import PyMongo

import json, pprint, logging

import numpy as np

from .responses.line_chart_response import LineChartResponse

bp = Blueprint('multihistory', __name__, url_prefix='/multihistory')

ERROR_NO_SUCH_SYMBOL = '{"error": "NoSuchSymbol"}'

logger = logging.getLogger(__name__)

@bp.route('/')
def symbol_history(symbol=None):

    symbols = request.args.get('symbols')
    logging.info('Fetching symbol history for: {}'.format(symbols))
    try:
        mongo = PyMongo(current_app)
        all_symbols = symbols.split(',')
        time_series_data = [basic_time_series(mongo.db.timeSeriesDailyAdjusted
            .find_one({'symbol': sym})['entries']) 
            for sym in all_symbols]

        # the data at this point is in the form: [ {'date1': close1 ... }, {'date2' : close2 ...} ]
        # list containing dicts with 'date' keys mapped to values 'close'.
        # squash into 1 list with all dates (labels) and n lists with all closes of n symbols
        encountered_dates = {}
        dates_for_symbols = []
        closes_for_symbols = []
        for symbol_data in time_series_data:
            for key_date in symbol_data:
                if not key_date in encountered_dates:
                    encountered_dates[key_date] = True
                    dates_for_symbols.append(key_date)
                    closes_for_symbols.append(get_date_array(time_series_data, key_date))

        # at this point, closes_for_symbols is in form [[date1sym1, date1sym2, ...], [date2sym1, date2sym2, ...]]
        # want it in the form: [[date1sym1, date2sym1, ...], [date1sym2, date2sym2, ...]]
        closes_for_symbols = np.array(closes_for_symbols).T.tolist()

        # if the first symbol encountered didn't cover all the dates, then these lists will all be out of 
        # order in the same manner. Sort them together based ond ates.
        dates_for_symbols = np.array(dates_for_symbols)
        indices = dates_for_symbols.argsort()
        dates_for_symbols = dates_for_symbols[indices].tolist()
        closes_for_symbols = [np.array(closes)[indices].tolist() for closes in closes_for_symbols]

        response = LineChartResponse('Prices over Time', x_axis_labels=dates_for_symbols, 
                                     y_axis_data=closes_for_symbols)
        return response.json_response()

    except (TypeError, AttributeError):
        logging.warning('Bad symbol provided')
        return ERROR_NO_SUCH_SYMBOL

def get_date_array(time_series_data, date):
    closes_for_all_symbols = []
    for symbol_data in time_series_data:
        if date in symbol_data:
            closes_for_all_symbols.append(symbol_data[date])
        else:
            closes_for_all_symbols.append(None)
    
    return closes_for_all_symbols

def basic_time_series(time_series):
    basic_series = dict()
    for entry in time_series:
        basic_series[entry['date']] = entry['close']
    return basic_series

