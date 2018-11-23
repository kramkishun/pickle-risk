from flask import Blueprint, current_app, request
from flask_pymongo import PyMongo

import json, pprint

bp = Blueprint('multihistory', __name__, url_prefix='/multihistory')

ERROR_NO_SUCH_SYMBOL = '{"error": "NoSuchSymbol"}'

@bp.route('/')
def symbol_history(symbol=None):

    try:
        mongo = PyMongo(current_app)
        all_symbols = request.args.get('symbols').split(',')
        pprint.pprint(all_symbols)

        time_series_data = [basic_time_series(mongo.db.timeSeriesDailyAdjusted.find_one({'symbol': sym})['entries']) for sym in all_symbols]
        return json.dumps(time_series_data)
    except TypeError:
        return ERROR_NO_SUCH_SYMBOL

def basic_time_series(time_series):
    basic_series = dict()
    for entry in time_series:
        basic_series[entry['date']] = entry['close']
    return basic_series

#TODO: Need to squash all data onto the same time axis 
